from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from account.auth.views import (CustomTokenObtainPairView, 
                                RegisterView, 
                                ChangePasswordView, 
                                ForgotPasswordView, 
                                ResetPasswordView,
                                EmailVerificationView,
                                EmailConfirmedView,
                                Verify2FAView,
                                )


app_name="auth"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("logout/", TokenBlacklistView.as_view(), name="auth-logout"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("reset-password/<str:uid>/<str:token>/", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("verify-email/", EmailVerificationView.as_view(), name="auth-verify-email"),
    path("confirm-email/<str:uid>/<str:token>/", EmailConfirmedView.as_view(), name="auth-confirm-email"),
    path("verify-2fa/", Verify2FAView.as_view(), name="auth-verify-2fa"),
    
]