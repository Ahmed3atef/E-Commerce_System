from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from account.auth.views import (CustomTokenObtainPairView, 
                                RegisterView, 
                                MeView, 
                                ChangePasswordView, 
                                ForgotPasswordView, 
                                ResetPasswordView,
                                EmailVerificationView,
                                EmailConfirmedView)

app_name = "account"

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="auth-logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-token_refresh"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("auth/reset-password/<str:uid>/<str:token>/", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("auth/verify-email/", EmailVerificationView.as_view(), name="auth-verify-email"),
    path("auth/confirm-email/<str:uid>/<str:token>/", EmailConfirmedView.as_view(), name="auth-confirm-email"),
    path("users/me/", MeView.as_view(), name="user-me"),
]