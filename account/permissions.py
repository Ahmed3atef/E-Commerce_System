from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller

class IsVerifiedSeller(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and user.is_seller
            and hasattr(user, "seller_profile")
            and user.seller_profile.is_verified
        )