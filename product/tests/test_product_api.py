import pytest
from django.urls import reverse
from rest_framework import status
from account.models import SellerProfile
from store.models.store import Store
from product.models.product import Product
from product.models.category import Category

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
        name="Test Store", 
        is_approved=True,
        is_active=True
    )

@pytest.fixture
def test_category(db):
    return Category.objects.create(name="Tech", slug="tech")

@pytest.mark.django_db
class TestProductAPI:
    
    def test_list_products_public(self, api_client, approved_store, test_category):
        # Only approved products should show to public
        Product.objects.create(
            store=approved_store, category=test_category, 
            name="Approved Phone", price=100.00, is_approved=True
        )
        Product.objects.create(
            store=approved_store, category=test_category, 
            name="Pending Phone", price=100.00, is_approved=False
        )
        
        url = reverse("product:product-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should only see 1 product
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Approved Phone"

    def test_seller_can_see_their_own_pending_products(self, api_client, product_owner, approved_store):
        api_client.force_authenticate(user=product_owner)
        Product.objects.create(
            store=approved_store, name="My Pending Product", price=50.00, is_approved=False
        )
        
        url = reverse("product:product-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert any(p["name"] == "My Pending Product" for p in response.data)

    def test_create_product_success(self, api_client, product_owner, approved_store, test_category):
        api_client.force_authenticate(user=product_owner)
        url = reverse("product:product-list")
        data = {
            "store": approved_store.id,
            "category": test_category.id,
            "name": "New Smartphone",
            "price": 899.99,
            "stock_quantity": 20
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name="New Smartphone").exists()
        assert Product.objects.get(name="New Smartphone").is_approved is False

    def test_update_product_owner_only(self, api_client, product_owner, approved_store, customer_user):
        product = Product.objects.create(
            store=approved_store, name="Old Name", price=10.00, is_approved=True
        )
        url = reverse("product:product-detail", kwargs={"pk": product.pk})
        
        # Try with random customer
        api_client.force_authenticate(user=customer_user)
        response = api_client.patch(url, {"name": "Hacked Name"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try with owner
        api_client.force_authenticate(user=product_owner)
        response = api_client.patch(url, {"name": "New Name"})
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.name == "New Name"

    def test_staff_approve_product(self, api_client, approved_store):
        product = Product.objects.create(store=approved_store, name="Waiting Approval", price=10.0)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff_user = User.objects.create(email="staff_prod@test.com", is_staff=True, role="staff")
        api_client.force_authenticate(user=staff_user)
        
        url = reverse("product:product-approve", kwargs={"pk": product.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        product.refresh_from_db()
        assert product.is_approved is True
        assert product.approved_at is not None

    def test_staff_reject_product(self, api_client, approved_store):
        product = Product.objects.create(store=approved_store, name="Bad Product", price=10.0)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff_user = User.objects.create(email="staff_rej@test.com", is_staff=True, role="staff")
        api_client.force_authenticate(user=staff_user)
        
        url = reverse("product:product-reject", kwargs={"pk": product.pk})
        data = {"rejection_reason": "Policy violation"}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.is_approved is False
        assert product.rejection_reason == "Policy violation"

    def test_delete_product_owner_only(self, api_client, product_owner, approved_store):
        product = Product.objects.create(store=approved_store, name="To Delete", price=10.00)
        api_client.force_authenticate(user=product_owner)
        
        url = reverse("product:product-detail", kwargs={"pk": product.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(pk=product.pk).exists()
