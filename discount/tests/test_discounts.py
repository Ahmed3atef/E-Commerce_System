import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from product.models.product import Product
from store.models.store import Store
from account.models import SellerProfile
from discount.models import Coupon, ProductDiscount

@pytest.fixture
def product(db_user):
    profile, _ = SellerProfile.objects.get_or_create(user=db_user)
    store = Store.objects.create(seller=profile, name="Discount Store", is_approved=True)
    return Product.objects.create(
        store=store, name="Sale Item", price=100.00, stock_quantity=10, is_approved=True
    )

@pytest.mark.django_db
class TestDiscountAPI:
    
    def test_coupon_validation(self, api_client, customer_user):
        coupon = Coupon.objects.create(
            code="SAVE10",
            discount_type="percentage",
            value=10.00,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
            min_purchase_amount=50.00
        )
        
        api_client.force_authenticate(user=customer_user)
        url = reverse("discount:coupon-apply")
        
        # Valid apply
        response = api_client.post(url, {"code": "SAVE10", "order_amount": 100.00})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["discount_amount"] == 10.00
        
        # Below min amount
        response = api_client.post(url, {"code": "SAVE10", "order_amount": 40.00})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_product_automatic_discount(self, product):
        # Create a direct product discount
        discount = ProductDiscount.objects.create(
            name="Flash Sale",
            discount_type="percentage",
            value=25.00,
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=1)
        )
        discount.products.add(product)
        
        assert product.get_discounted_price() == 75.00 # 100 - 25%

    def test_order_with_coupon_integration(self, api_client, customer_user, product):
        from address.models import Address
        from django.contrib.contenttypes.models import ContentType
        from account.models import CustomerProfile
        
        # Setup address
        profile, _ = CustomerProfile.objects.get_or_create(user=customer_user)
        addr = Address.objects.create(
            content_type=ContentType.objects.get_for_model(CustomerProfile),
            object_id=profile.id,
            type="home", country="EG", city="Cairo", street="Test"
        )
        
        # Setup coupon
        Coupon.objects.create(
            code="WELCOME20",
            discount_type="fixed",
            value=20.00,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1)
        )
        
        api_client.force_authenticate(user=customer_user)
        url = reverse("order:order-list")
        data = {
            "shipping_address": addr.id,
            "billing_address": addr.id,
            "items": [{"product": product.id, "quantity": 1}],
            "coupon_code": "WELCOME20"
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert float(response.data["total_amount"]) == 80.00 # 100 - 20
        assert float(response.data["discount_amount"]) == 20.00
