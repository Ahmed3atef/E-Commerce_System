import pytest
from rest_framework import status

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
