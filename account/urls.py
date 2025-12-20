from django.urls import path, include
from .views import UsersStuffListView, MeView, CustomerProfileViewSet, SellerProfileViewSet, StaffProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("customer-profile", CustomerProfileViewSet)
router.register("seller-profile", SellerProfileViewSet)
router.register("staff-profile", StaffProfileViewSet)

app_name = "account"

urlpatterns = [
    path("stuff/", UsersStuffListView.as_view(), name="users-stuff"),
    path("me/", MeView.as_view(), name="user-me"),
    path("",include(router.urls))
]
