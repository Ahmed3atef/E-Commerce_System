import pytest
from django.urls import reverse

@pytest.fixture
def customer_profile(customer_user):
    from account.models import CustomerProfile
    return CustomerProfile.objects.get_or_create(user=customer_user)[0]

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