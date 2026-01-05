import pytest
from django.urls import reverse

@pytest.fixture
def register_endpoint(api_client):
    def request_has_body(body):
        return api_client.post(reverse("auth:auth-register"), body)
    return request_has_body

@pytest.fixture
def auth_endpoints(api_client):
    def login_endpoint(payload):
            return  api_client.post(reverse("auth:auth-login"), payload)
    def refresh_endpoint(payload):
            return  api_client.post(reverse("auth:auth-token_refresh"), payload)
    def logout_endpoint(payload):
            return  api_client.post(reverse("auth:auth-logout"), payload)
    return {"login": login_endpoint, "refresh": refresh_endpoint, "logout": logout_endpoint}

@pytest.fixture
def change_password_endpoint(api_client):
    def request_has_body(body={}, token=None):
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return api_client.post(reverse("auth:auth-change-password"), body)
    return request_has_body

@pytest.fixture
def email_verification_endpoints(api_client):
    def email_verify(body={}):
        return api_client.post(reverse("auth:auth-verify-email"), body)
    def email_confirm(uid, token):
        return api_client.get(reverse("auth:auth-confirm-email", args=[uid, token]))
    return {"email_verify": email_verify, "email_confirm": email_confirm}

@pytest.fixture
def forgot_password_endpoint(api_client):
    def send_change_password_email(body={}):
        return api_client.post(reverse("auth:auth-forgot-password"), body)
    
    def rest_passord_get(uid, token):
        return api_client.get(reverse("auth:auth-reset-password", args=[uid, token]))
    
    def rest_passord_post(uid, token, body={}):
        return api_client.post(reverse("auth:auth-reset-password", args=[uid, token]), body)

    return {"send_change_password_email": send_change_password_email, "rest_passord_get": rest_passord_get, "rest_passord_post": rest_passord_post}

@pytest.fixture
def verify_2fa_endpoint(api_client):
    def request_has_body(body):
        return api_client.post(reverse("auth:auth-verify-2fa"), body)
    return request_has_body
