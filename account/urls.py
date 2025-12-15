from django.urls import path,include
from account.auth.views import CustomTokenObtainPairView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from account.views import SellerAdminViewSet, UserViewSet, MeView


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("admin/sellers", SellerAdminViewSet, basename="admin-sellers")



urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", MeView.as_view(), name="me"),
    path("", include(router.urls))
]