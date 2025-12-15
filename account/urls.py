from django.urls import path,include
from account.auth.views import CustomTokenObtainPairView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenBlacklistView
from rest_framework.routers import DefaultRouter
from account.auth.views import UserViewSet
# from account.views import SellerAdminViewSet, UserViewSet, MeView


router = DefaultRouter()
router.register("user", UserViewSet, basename="user")


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls))
]