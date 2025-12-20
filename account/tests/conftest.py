import pytest
from rest_framework.test import APIClient
from django.urls import reverse
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

@pytest.fixture
def customer_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create(
        email="customer@test.com",
        password=make_password("CustomerPass123"),
        phone="+201111111111",
        role="customer"
    )
    return user

@pytest.fixture
def customer_profile(customer_user):
    from account.models import CustomerProfile
    return CustomerProfile.objects.get_or_create(user=customer_user)[0]

@pytest.fixture
def register_endpoint(api_client):
    def request_has_body(body):
        return api_client.post(reverse("auth:auth-register"), body)
    return request_has_body


@pytest.fixture
def auth_endpoints(api_client):
    def login_endpoint(payload):
            return  api_client.post(reverse("auth:auth-login"), payload)
    def refresh_endpoint(payload):
            return  api_client.post(reverse("auth:auth-token_refresh"), payload)
    def logout_endpoint(payload):
            return  api_client.post(reverse("auth:auth-logout"), payload)
    return {"login": login_endpoint, "refresh": refresh_endpoint, "logout": logout_endpoint}


@pytest.fixture
def me_endpoint(api_client):
    def get_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.get(reverse("account:user-me"))
    def post_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.post(reverse("account:user-me"), body)
    def put_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.put(reverse("account:user-me"), body)
    def patch_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.patch(reverse("account:user-me"), body)
    return {"get": get_method, "post": post_method, "put": put_method, "patch": patch_method}



@pytest.fixture
def users_stuff_endpoint(api_client):
    def get_list(token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return api_client.get(reverse("account:users-stuff"))
    return get_list