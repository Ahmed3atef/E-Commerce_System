import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def db_user():
    user = User.objects.create(
        email = "seller@test.com",
        password =  make_password("StrongPass123"),
        # password2 =  "StrongPass123",
        phone =  "+201234567890",
        role = "seller"
    )
    
    return user
