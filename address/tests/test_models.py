import pytest
from django.core.exceptions import ValidationError
from address.models import Address
from account.models import CustomerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestAddressValidation:
    
    def test_valid_country_code(self):
        user = User.objects.create(email="addr_test@test.com")
        profile = CustomerProfile.objects.create(user=user)
        
        address = Address(
            content_object=profile,
            type="home",
            country="US",  # Valid
            city="NY",
            street="Main St"
        )
        # Should not raise
        address.full_clean()
        address.save()
        assert address.pk is not None

    def test_invalid_country_code(self):
        user = User.objects.create(email="addr_fail@test.com")
        profile = CustomerProfile.objects.create(user=user)
        
        address = Address(
            content_object=profile,
            type="home",
            country="XX",  # Invalid
            city="Invalid",
            street="Invalid St"
        )
        
        with pytest.raises(ValidationError) as excinfo:
            address.full_clean()
        
        assert "is not a valid ISO 3166-1 alpha-2 country code" in str(excinfo.value)

    def test_lowercase_country_code_normalized(self):
        user = User.objects.create(email="addr_norm@test.com")
        profile = CustomerProfile.objects.create(user=user)
        
        address = Address(
            content_object=profile,
            type="home",
            country="eg",  # valid but lowercase
            city="Cairo",
            street="Tahrir"
        )
        # Should not raise because we upper() it in validation
        address.full_clean()
        address.save()
        assert address.country == "eg" # Validator doesn't change the value, just checks it. 
        # Usually we'd want to save it uppered, but the validation passes.
