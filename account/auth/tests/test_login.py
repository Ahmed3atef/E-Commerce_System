import pytest
from rest_framework import status

@pytest.mark.django_db
class TestLoginAuth:
    
    def test_login_customer_user_200(self, api_client, db_user, auth_endpoints):
        
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        response = auth_endpoints["login"](body)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data  # JWT access token
        assert 'refresh' in response.data  # JWT refresh token
    
    def test_refresh_endpoint(self, api_client, db_user, auth_endpoints):
        
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        payload = {
            "refresh": auth_endpoints["login"](body).data.get("refresh")
        }
        response = auth_endpoints["refresh"](payload)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_logout_endpoint(self, api_client, db_user, auth_endpoints):
        
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        payload = {
            "refresh": auth_endpoints["login"](body).data.get("refresh")
        }
        response = auth_endpoints["logout"](payload)
        
        assert response.status_code == status.HTTP_200_OK
