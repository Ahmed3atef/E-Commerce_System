import pytest
from rest_framework import status

@pytest.fixture
def register_endpoint(api_client):
    def request_has_body(body):
        return api_client.post('/api/account/auth/register/', body)
    return request_has_body


@pytest.mark.django_db
class TestRegisterAuth:
    def test_register_new_seller_user_201(self, api_client, register_endpoint):
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123",
            "password2": "StrongPass123",
            "phone": "+201234567890",
            "role": "seller"
        }
        response = register_endpoint(body)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_register_new_seller_user_bad_request_400(self, api_client, register_endpoint):
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123",
            "phone": "+201234567890",
            "role": "seller"
        }
        response = register_endpoint(body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_register_new_default_role_user_201(self, api_client, register_endpoint):
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123",
            "password2": "StrongPass123",
            "phone": "+201234567890",
        }
        response = register_endpoint(body)
        assert response.status_code == status.HTTP_201_CREATED
        
    def test_register_new_customer_role_user_201(self, api_client, register_endpoint):
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123",
            "password2": "StrongPass123",
            "phone": "+201234567890",
            "role": "customer"
        }
        response = register_endpoint( body)
        
        assert response.status_code == status.HTTP_201_CREATED
        
    def test_register_new_stuff_role_user_400(self, api_client, register_endpoint):
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123",
            "password2": "StrongPass123",
            "phone": "+201234567890",
            "role": "staff"
        }
        response = register_endpoint(body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST




@pytest.fixture
def login_endpoint(api_client):
    def request_has_payload(payload):
            return  api_client.post('/api/account/auth/login/', payload)
    return request_has_payload

@pytest.fixture
def refresh_endpoint(api_client):
    def request_has_payload(payload):
            return  api_client.post('/api/account/auth/refresh/', payload)
    return request_has_payload

@pytest.mark.django_db
class TestLoginAuth:
    
    def test_login_customer_user_200(self, api_client,db_user, login_endpoint):
        
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        response = login_endpoint(body)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data  # JWT access token
        assert 'refresh' in response.data  # JWT refresh token
    
    def test_refresh_endpoint(self,api_client,db_user, login_endpoint, refresh_endpoint):
        
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        payload = {
            "refresh": login_endpoint(body).data.get("refresh")
        }
        response = refresh_endpoint(payload)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        