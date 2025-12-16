from django.urls import path
from .views import UsersStuffListView, MeView


app_name = "account"

urlpatterns = [
    path("stuff/", UsersStuffListView.as_view(), name="users-stuff"),
    path("me/", MeView.as_view(), name="user-me"),
]
