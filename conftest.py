import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def db_user(db):
    user = User.objects.create(
        email = "seller@test.com",
        password =  make_password("StrongPass123"),
        phone =  "+201234567890",
        role = "seller"
    )
    return user

@pytest.fixture
def customer_user(db):
    user = User.objects.create(
        email="customer@test.com",
        password=make_password("CustomerPass123"),
        phone="+201111111111",
        role="customer"
    )
    return user