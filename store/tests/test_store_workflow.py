import pytest
from django.urls import reverse
from rest_framework import status
from account.models import SellerProfile
from store.models.store import Store
from product.models.product import Product

@pytest.mark.django_db
class TestStoreWorkflow:
    
    def test_seller_request_store_fails_without_onboarding(self, api_client, db_user):
        # db_user is a seller by default in conftest? Let's check.
        # conftest db_user has role 'seller'
        
        # Ensure profile exists
        profile, _ = SellerProfile.objects.get_or_create(user=db_user)
        profile.onboarding_completed = False
        profile.is_verified = False
        profile.save()
        
        api_client.force_authenticate(user=db_user)
        url = reverse("store:store-list")
        data = {"name": "Test Store"}
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # The validator checks is_verified first
        assert "verified" in str(response.data) or "onboarding" in str(response.data)

    def test_seller_request_store_success_after_onboarding(self, api_client, db_user):
        profile, _ = SellerProfile.objects.get_or_create(user=db_user)
        profile.onboarding_completed = True
        profile.is_verified = True
        profile.save()
        
        api_client.force_authenticate(user=db_user)
        url = reverse("store:store-list")
        data = {"name": "Legit Store"}
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Store.objects.filter(name="Legit Store").exists()
        assert Store.objects.get(name="Legit Store").is_approved is False

    def test_staff_approve_store(self, api_client, db_user):
        # Create a store first
        profile, _ = SellerProfile.objects.get_or_create(user=db_user)
        store = Store.objects.create(seller=profile, name="Pending Store")
        
        # Logout seller, Login staff
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff_user = User.objects.create(email="staff@test.com", is_staff=True, role="staff")
        api_client.force_authenticate(user=staff_user)
        
        url = reverse("store:store-approve", kwargs={"pk": store.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        store.refresh_from_db()
        assert store.is_approved is True
        assert store.approved_at is not None

    def test_add_product_to_unapproved_store_fails(self, api_client, db_user):
        profile, _ = SellerProfile.objects.get_or_create(user=db_user)
        store = Store.objects.create(seller=profile, name="Unapproved")
        
        api_client.force_authenticate(user=db_user)
        url = reverse("product:product-list")
        data = {
            "store": store.id,
            "name": "Iphone 13",
            "price": 999.99,
            "stock_quantity": 10
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This store is not approved yet" in str(response.data)

    def test_add_product_to_approved_store_success(self, api_client, db_user):
        profile, _ = SellerProfile.objects.get_or_create(user=db_user)
        store = Store.objects.create(seller=profile, name="Approved Shop", is_approved=True)
        
        api_client.force_authenticate(user=db_user)
        url = reverse("product:product-list")
        data = {
            "store": store.id,
            "name": "Iphone 15",
            "price": 1200.00,
            "stock_quantity": 5
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name="Iphone 15").exists()
