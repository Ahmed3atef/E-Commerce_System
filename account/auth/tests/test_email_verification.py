import pytest
from rest_framework import status
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from account.auth.utils import email_verification_token_generator

@pytest.mark.django_db
class TestEmailVerification:
    def test_send_email_verification_200(self, api_client, db_user, email_verification_endpoints):
        
        body = {
            "email": "seller@test.com",
        }
        
        response = email_verification_endpoints["email_verify"](body)
        
        assert response.status_code == status.HTTP_200_OK
        
    def test_confirm_email_200(self, api_client, db_user, email_verification_endpoints):
        
        token = email_verification_token_generator.make_token(db_user)
        uid = urlsafe_base64_encode(force_bytes(db_user.pk))
        
        response = email_verification_endpoints["email_confirm"](uid, token)
        
        assert response.status_code == status.HTTP_200_OK
        
        db_user.refresh_from_db()
        assert db_user.is_email_verified == True

    def test_email_verification_token_replay(self, api_client, db_user, email_verification_endpoints):
         # 1. Generate token
        token = email_verification_token_generator.make_token(db_user)
        uid = urlsafe_base64_encode(force_bytes(db_user.pk))
        
        # 2. Verify Email (First Use)
        response = email_verification_endpoints["email_confirm"](uid, token)
        assert response.status_code == status.HTTP_200_OK
        
        db_user.refresh_from_db()
        assert db_user.is_email_verified == True

        # 3. Try to Verify Again (Replay)
        # This SHOULD fail because verifying changes the hash state (is_email_verified True -> token invalid for False)
        response_replay = email_verification_endpoints["email_confirm"](uid, token)
        
        assert response_replay.status_code == status.HTTP_400_BAD_REQUEST
