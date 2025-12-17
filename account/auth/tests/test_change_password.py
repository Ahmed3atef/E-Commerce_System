import pytest
from rest_framework import status

@pytest.mark.django_db
class TestChangePassword:
    def test_change_password_endpoint_200(self, api_client, db_user, change_password_endpoint, auth_endpoints):
        login_body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        login_response = auth_endpoints["login"](login_body)
        access_token = login_response.data.get("access")
        
        body = {"old_password": "StrongPass123", 
                "new_password": "NewPass123", 
                "new_password2": "NewPass123"}
        
        response = change_password_endpoint(body, access_token)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("email") == "seller@test.com"
        assert response.data.get("role") == "seller"
        assert response.data.get("is_phone_verified") == False
