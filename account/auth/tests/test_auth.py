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
def auth_endpoints(api_client):
    def login_endpoint(payload):
            return  api_client.post('/api/account/auth/login/', payload)
    def refresh_endpoint(payload):
            return  api_client.post('/api/account/auth/refresh/', payload)
    def logout_endpoint(payload):
            return  api_client.post('/api/account/auth/logout/', payload)
    return {"login": login_endpoint, "refresh": refresh_endpoint, "logout": logout_endpoint}

@pytest.mark.django_db
class TestLoginAuth:
    
    def test_login_customer_user_200(self, api_client,db_user, auth_endpoints):
        
        body = {
            "email": "seller@test.com",
            "password": "StrongPass123"
        }
        
        response = auth_endpoints["login"](body)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data  # JWT access token
        assert 'refresh' in response.data  # JWT refresh token
    
    def test_refresh_endpoint(self,api_client,db_user, auth_endpoints):
        
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
             
        
@pytest.fixture
def me_endpoint(api_client):
    def get_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.get('/api/account/users/me/')
    def post_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.post('/api/account/users/me/', body)
    def put_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.put('/api/account/users/me/', body)
    def patch_method(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return  api_client.patch('/api/account/users/me/', body)
    return {"get": get_method, "post": post_method, "put": put_method, "patch": patch_method}

@pytest.fixture
def change_password_endpoint(api_client):
    def request_has_body(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return api_client.post('/api/account/auth/change-password/', body)
    return request_has_body

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
