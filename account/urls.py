from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from account.auth.views import (CustomTokenObtainPairView, 
                                RegisterView, 
                                MeView, 
                                ChangePasswordView, 
                                ForgotPasswordView, 
                                ResetPasswordView)

app_name = "account"

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="auth-logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-token_refresh"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("users/me/", MeView.as_view(), name="user-me"),
]