import pytest
from django.urls import reverse
from rest_framework import status
from account.models import CustomerProfile
from address.models import Address

@pytest.mark.django_db
class TestCustomerProfile:
    
    def test_create_customer_profile(self, api_client, db_user):
        # Only staff can create profiles via this endpoint usually, 
        # but let's see how the viewset is configured.
        # It's using CreateModelMixin without specific permission overrides in the viewset itself,
        # so it relies on global permissions.
        
        # We need a user with role='customer' but NO profile yet.
        from django.contrib.auth import get_user_model
        User = get_user_model()
        new_user = User.objects.create(email="new_customer@test.com", role="customer")
        
        url = reverse("account:customerprofile-list")
        data = {
            "user": new_user.id,
            "preferred_language": "ar",
            "marketing_opt_in": True
        }
        
        # Using a staff user to create
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert CustomerProfile.objects.filter(user=new_user).exists()

    def test_retrieve_customer_profile(self, api_client, customer_profile, db_user):
        url = reverse("account:customerprofile-detail", kwargs={"pk": customer_profile.pk})
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == customer_profile.user.id

    def test_update_customer_profile(self, api_client, customer_profile, db_user):
        url = reverse("account:customerprofile-detail", kwargs={"pk": customer_profile.pk})
        
        data = {
            "is_blocked": True,
            "blocked_reason": "Testing suspension",
            "preferred_language": "fr"
        }
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        customer_profile.refresh_from_db()
        assert customer_profile.is_blocked is True
        assert customer_profile.blocked_reason == "Testing suspension"
        assert customer_profile.preferred_language == "fr"

    def test_delete_customer_profile(self, api_client, customer_profile, db_user):
        url = reverse("account:customerprofile-detail", kwargs={"pk": customer_profile.pk})
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomerProfile.objects.filter(pk=customer_profile.pk).exists()

    def test_customer_profile_with_address(self, api_client, customer_profile, db_user):
        # Create an address manually for the profile
        address = Address.objects.create(
            content_object=customer_profile,
            type="home",
            country="EG",
            city="Cairo",
            street="Tahrir St",
            postal_code="12345"
        )
        
        url = reverse("account:customerprofile-detail", kwargs={"pk": customer_profile.pk})
        
        db_user.is_staff = True
        db_user.save()
        api_client.force_authenticate(user=db_user)
        
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["address"]) == 1
        assert response.data["address"][0]["city"] == "Cairo"
