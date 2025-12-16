import pytest
from rest_framework import status

      
@pytest.mark.django_db
class TestMeView:
    
    def test_me_endpoint_get_200(self, api_client, db_user, me_endpoint, auth_endpoints):
        login_body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        login_response = auth_endpoints["login"](login_body)
        access_token = login_response.data.get("access")
        
        response = me_endpoint["get"]({}, access_token)
        assert response.status_code == status.HTTP_200_OK
    
    def test_me_endpoint_put_200(self, api_client, db_user, me_endpoint, auth_endpoints):
        login_body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        login_response = auth_endpoints["login"](login_body)
        access_token = login_response.data.get("access")
        
        response = me_endpoint["put"]({"phone": "+201234567890"}, access_token)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("phone") == "+201234567890"
        
    def test_me_endpoint_patch_200(self, api_client, db_user, me_endpoint, auth_endpoints):
        login_body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        login_response = auth_endpoints["login"](login_body)
        access_token = login_response.data.get("access")
        
        response = me_endpoint["patch"]({"phone": "+201234567890"}, access_token)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("phone") == "+201234567890"    
        
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


@pytest.mark.django_db
class TestUsersStuffList:
    def test_list_users_staff_200(self, api_client, db_user, users_stuff_endpoint, auth_endpoints):
        # Make user staff
        db_user.role = "staff"
        db_user.save()
        
        # Login
        login_body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        login_response = auth_endpoints["login"](login_body)
        access_token = login_response.data.get("access")
        
        response = users_stuff_endpoint(token=access_token)
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_non_staff_403(self, api_client, db_user, users_stuff_endpoint, auth_endpoints):
        # Login (User is not staff by default)
        login_body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        login_response = auth_endpoints["login"](login_body)
        access_token = login_response.data.get("access")
        
        response = users_stuff_endpoint(token=access_token)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_unauthenticated_401(self, api_client, users_stuff_endpoint):
        response = users_stuff_endpoint()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED