import pytest
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core import mail


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
@pytest.mark.django_db
class TestEmailVerification:
    def test_send_email_verification_200(self, api_client, db_user,email_verification_endpoints):
        
        body = {
            "email": "seller@test.com",
        }
        
        response = email_verification_endpoints["email_verify"](body)
        
        assert response.status_code == status.HTTP_200_OK
        
    def test_confirm_email_200(self, api_client, db_user, email_verification_endpoints):
        
        token = default_token_generator.make_token(db_user)
        uid = urlsafe_base64_encode(force_bytes(db_user.pk))
        
        response = email_verification_endpoints["email_confirm"](uid, token)
        
        assert response.status_code == status.HTTP_200_OK
        
        db_user.refresh_from_db()
        assert db_user.is_email_verified == True

@pytest.mark.django_db
class TestForgetPassword:
    def test_forget_password_send_email_200(self, api_client, db_user, forgot_password_endpoint):
        body = {
            "email": "seller@test.com",
        }
        
        response = forgot_password_endpoint["send_change_password_email"](body)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == 'Password Reset'
        assert mail.outbox[0].to == ['seller@test.com']
        assert response.data.get("message") == 'If email exists, reset link was sent'
    
    def test_forget_password_send_email_404(self, api_client, db_user, forgot_password_endpoint):
        body = {
            "email": "seller123@test.com",
        }
        
        response = forgot_password_endpoint["send_change_password_email"](body)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data.get("detail") == "User with this email does not exist"
        
    
    def test_reset_password_get_200(self, api_client, db_user, forgot_password_endpoint):
        token = default_token_generator.make_token(db_user)
        uid = urlsafe_base64_encode(force_bytes(db_user.pk))
        
        response = forgot_password_endpoint["rest_passord_get"](uid, token)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("uid") == uid
        assert response.data.get("token") == token
    
    def test_reset_password_post_200(self, api_client, db_user, forgot_password_endpoint):
        token = default_token_generator.make_token(db_user)
        uid = urlsafe_base64_encode(force_bytes(db_user.pk))
        body = {
            "password": "NewPass123",
            "password2": "NewPass123"
        }
        
        response = forgot_password_endpoint["rest_passord_post"](uid, token, body)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("message") == "Password reset successfully"
        
    