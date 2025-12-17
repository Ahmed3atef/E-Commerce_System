import pytest
from rest_framework import status
from django.core import mail
from django.core.cache import cache
from account.auth.utils import generate_2fa_code

@pytest.mark.django_db
class TestTwoFactorAuth:
    
    def test_login_with_2fa_enabled_returns_challenge(self, api_client, db_user, auth_endpoints):
        # Enable 2FA for the user
        db_user.is_2fa_enabled = True
        db_user.save()
        
        body = {
            "email": db_user.email,
            "password": "StrongPass123"
        }
        
        response = auth_endpoints["login"](body)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("requires_2fa") is True
        assert response.data.get("user_id") == db_user.id
        assert "message" in response.data
        # Verify email was sent
        assert len(mail.outbox) == 1
        assert "Your 2FA Login Code" in mail.outbox[0].subject

    def test_login_with_2fa_disabled_returns_tokens(self, api_client, db_user, auth_endpoints):
        # Ensure 2FA is disabled (default)
        db_user.is_2fa_enabled = False
        db_user.save()
        
        body = {
            "email": db_user.email,
            "password": "StrongPass123"
        }
        
        response = auth_endpoints["login"](body)
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "requires_2fa" not in response.data

    def test_verify_2fa_success(self, api_client, db_user, verify_2fa_endpoint):
        # 1. Generate a code for the user
        code = generate_2fa_code(db_user.id)
        
        # 2. Verify it
        body = {
            "user_id": db_user.id,
            "code": code
        }
        response = verify_2fa_endpoint(body)
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        
        # 3. Code should be deleted from cache
        assert cache.get(f"2fa_code_{db_user.id}") is None

    def test_verify_2fa_invalid_code(self, api_client, db_user, verify_2fa_endpoint):
        generate_2fa_code(db_user.id)
        
        body = {
            "user_id": db_user.id,
            "code": "000000" # Wrong code
        }
        response = verify_2fa_endpoint(body)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "code" in response.data

    def test_verify_2fa_rate_limiting(self, api_client, db_user, verify_2fa_endpoint):
        generate_2fa_code(db_user.id)
        
        body = {
            "user_id": db_user.id,
            "code": "000000"
        }
        
        # 5 failed attempts
        for _ in range(5):
            response = verify_2fa_endpoint(body)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
        # 6th attempt should trigger rate limiting message
        response = verify_2fa_endpoint(body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Too many attempts" in response.data["code"][0]
