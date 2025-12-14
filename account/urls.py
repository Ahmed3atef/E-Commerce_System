from django.urls import path,include
from account.auth.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()




urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls))
]