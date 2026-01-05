from rest_framework import permissions

class IsCouponOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.store and hasattr(request.user, 'seller_profile'):
            return obj.store.seller == request.user.seller_profile
        return False

class IsVerifiedSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        if hasattr(request.user, 'seller_profile'):
            return request.user.seller_profile.is_verified
        return False
