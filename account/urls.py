from django.urls import path
from account.auth.views import CustomTokenObtainPairView, RegisterView, MeView
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", MeView.as_view(), name="user-me"),
]