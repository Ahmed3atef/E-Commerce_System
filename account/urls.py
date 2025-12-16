from django.urls import path, include

app_name = "account"

urlpatterns = [
    path("auth/", include("account.auth.urls")),
]
