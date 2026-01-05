import pytest
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core import mail

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

    def test_reset_password_token_invalidation_after_use(self, api_client, db_user, forgot_password_endpoint):
        # 1. Generate token
        token = default_token_generator.make_token(db_user)
        uid = urlsafe_base64_encode(force_bytes(db_user.pk))
        
        # 2. Reset Password (First Use)
        body = {
            "password": "NewPass123",
            "password2": "NewPass123"
        }
        response = forgot_password_endpoint["rest_passord_post"](uid, token, body)
        assert response.status_code == status.HTTP_200_OK

        # 3. Try to Reset Again (Replay)
        response_replay = forgot_password_endpoint["rest_passord_post"](uid, token, body)
        
        # This SHOULD fail because changing password invalidates the token
        assert response_replay.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response_replay.data
