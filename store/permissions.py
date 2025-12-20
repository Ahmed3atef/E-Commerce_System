from rest_framework import permissions

class IsStoreOwner(permissions.BasePermission):
    """
    Permission to allow only the owner of the store to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.seller.user == request.user

class IsStaffUser(permissions.BasePermission):
    """
    Permission to allow only staff members.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
