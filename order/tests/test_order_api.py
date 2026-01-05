import pytest
from django.urls import reverse
from rest_framework import status
from account.models import SellerProfile
from store.models.store import Store
from product.models.product import Product
from order.models import Order, OrderItem
from address.models import Address
from django.contrib.contenttypes.models import ContentType

@pytest.fixture
def product_owner(db_user):
    profile, _ = SellerProfile.objects.get_or_create(user=db_user)
    profile.onboarding_completed = True
    profile.is_verified = True
    profile.save()
    return db_user

@pytest.fixture
def approved_store(product_owner):
    return Store.objects.create(
        seller=product_owner.seller_profile, 
        name="Order Test Store", 
        is_approved=True,
        is_active=True
    )

@pytest.fixture
def test_product(approved_store):
    return Product.objects.create(
        store=approved_store,
        name="Test Product",
        price=100.00,
        stock_quantity=10,
        is_active=True,
        is_approved=True
    )

@pytest.fixture
def test_address(customer_user):
    from account.models import CustomerProfile
    profile, _ = CustomerProfile.objects.get_or_create(user=customer_user)
    return Address.objects.create(
        content_type=ContentType.objects.get_for_model(CustomerProfile),
        object_id=profile.id,
        type=Address.Type.HOME,
        country="EG",
        city="Cairo",
        street="123 Street",
        postal_code="12345"
    )

@pytest.mark.django_db
class TestOrderAPI:
    
    def test_customer_create_order_success(self, api_client, customer_user, test_product, test_address):
        api_client.force_authenticate(user=customer_user)
        url = reverse("order:order-list")
        data = {
            "shipping_address": test_address.id,
            "billing_address": test_address.id,
            "items": [
                {"product": test_product.id, "quantity": 2}
            ]
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check order exists
        order = Order.objects.get(user=customer_user)
        assert order.total_amount == 200.00 # 2 * 100
        
        # Check item exists
        assert OrderItem.objects.filter(order=order, product=test_product).exists()
        
        # Check stock reduction
        test_product.refresh_from_db()
        assert test_product.stock_quantity == 8

    def test_create_order_insufficient_stock_fails(self, api_client, customer_user, test_product, test_address):
        api_client.force_authenticate(user=customer_user)
        url = reverse("order:order-list")
        data = {
            "shipping_address": test_address.id,
            "billing_address": test_address.id,
            "items": [
                {"product": test_product.id, "quantity": 11} # Stock is 10
            ]
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Not enough stock" in str(response.data)

    def test_seller_can_see_order_with_their_product(self, api_client, product_owner, customer_user, test_product, test_address):
        # Create order first
        order = Order.objects.create(user=customer_user, total_amount=100)
        OrderItem.objects.create(
            order=order, product=test_product, quantity=1, price=100, store=test_product.store
        )
        
        # Authenticate as seller
        api_client.force_authenticate(user=product_owner)
        url = reverse("order:order-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["order_number"] == order.order_number

    def test_customer_only_sees_own_orders(self, api_client, customer_user, db_user, test_product):
        # Create an order for a different user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create(email="other@test.com", password="Pass123", role="customer")
        Order.objects.create(user=other_user, total_amount=50)
        
        # Authenticate as our customer
        api_client.force_authenticate(user=customer_user)
        url = reverse("order:order-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_seller_update_order_status(self, api_client, product_owner, customer_user, test_product):
        order = Order.objects.create(user=customer_user, total_amount=100)
        OrderItem.objects.create(
            order=order, product=test_product, quantity=1, price=100, store=test_product.store
        )
        
        api_client.force_authenticate(user=product_owner)
        url = reverse("order:order-update-status", kwargs={"pk": order.pk})
        response = api_client.patch(url, {"status": "processing"})
        
        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == "processing"

    def test_other_seller_cannot_update_order_status(self, api_client, customer_user, test_product):
        order = Order.objects.create(user=customer_user, total_amount=100)
        OrderItem.objects.create(
            order=order, product=test_product, quantity=1, price=100, store=test_product.store
        )
        
        # Create another seller
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_seller = User.objects.create(email="other_seller@test.com", role="seller")
        profile = SellerProfile.objects.create(user=other_seller, display_name="Other Shop", is_verified=True)
        
        api_client.force_authenticate(user=other_seller)
        url = reverse("order:order-update-status", kwargs={"pk": order.pk})
        response = api_client.patch(url, {"status": "shipped"})
        
        # They should get 404 because get_queryset filters them out, or 403 if it was in queryset
        # In our viewset, get_queryset filters orders if seller doesn't have products in it.
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_cancel_order_restores_stock(self, api_client, customer_user, test_product, test_address):
        # Create order
        api_client.force_authenticate(user=customer_user)
        url_create = reverse("order:order-list")
        data = {
            "shipping_address": test_address.id,
            "billing_address": test_address.id,
            "items": [{"product": test_product.id, "quantity": 5}]
        }
        response = api_client.post(url_create, data, format='json')
        order_id = response.data['id']
        test_product.refresh_from_db()
        assert test_product.stock_quantity == 5 # 10 - 5
        
        # Cancel order
        url_cancel = reverse("order:order-cancel", kwargs={"pk": order_id})
        response = api_client.post(url_cancel)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify status and stock
        order = Order.objects.get(id=order_id)
        assert order.status == "cancelled"
        test_product.refresh_from_db()
        assert test_product.stock_quantity == 10 # Restored
