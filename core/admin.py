from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    ordering = ("email",)
    list_display = (
        "email",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_phone_verified",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = ("email", "phone")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "phone", "is_phone_verified")},
        ),
        (
            "Role & Permissions",
            {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")
