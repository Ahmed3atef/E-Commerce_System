import pytest
from django.urls import reverse
from rest_framework import status
from account.models import SellerProfile
from address.models import Address

@pytest.mark.django_db
class TestSellerProfile:
    
    def test_create_seller_profile(self, api_client, db_user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        new_user = User.objects.create(email="new_seller@test.com", role="seller")
        
        url = reverse("account:sellerprofile-list")
        data = {
            "user": new_user.id,
            "seller_type": "individual",
            "display_name": "New Seller Store",
            "preferred_language": "en"
        }
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert SellerProfile.objects.filter(user=new_user).exists()

    def test_retrieve_seller_profile(self, api_client, db_user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        seller_user = User.objects.create(email="seller_test@test.com", role="seller")
        profile = SellerProfile.objects.create(user=seller_user, display_name="Test Store")
        
        url = reverse("account:sellerprofile-detail", kwargs={"pk": profile.pk})
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["display_name"] == "Test Store"

    def test_update_seller_profile_block(self, api_client, db_user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        seller_user = User.objects.create(email="seller_block@test.com", role="seller")
        profile = SellerProfile.objects.create(user=seller_user, display_name="To Be Blocked")
        
        url = reverse("account:sellerprofile-detail", kwargs={"pk": profile.pk})
        
        data = {
            "is_blocked": True,
            "blocked_reason": "Policy violation",
            "is_verified": True
        }
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        profile.refresh_from_db()
        assert profile.is_blocked is True
        assert profile.blocked_reason == "Policy violation"
        assert profile.is_verified is True

    def test_seller_profile_with_address(self, api_client, db_user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        seller_user = User.objects.create(email="seller_addr@test.com", role="seller")
        profile = SellerProfile.objects.create(user=seller_user, display_name="Store with Address")
        
        # Create an address for the seller
        Address.objects.create(
            content_object=profile,
            type="store",
            country="US",
            city="New York",
            street="5th Ave",
            postal_code="10001"
        )
        
        url = reverse("account:sellerprofile-detail", kwargs={"pk": profile.pk})
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["address"]) == 1
        assert response.data["address"][0]["type"] == "store"
        assert response.data["address"][0]["city"] == "New York"
