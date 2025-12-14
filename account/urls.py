from django.urls import path,include
from account.auth.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from account.views import UserViewSet


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")



urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls))
]