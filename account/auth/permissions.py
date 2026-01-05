from rest_framework.permissions import BasePermission



class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_platform_staff
        )

class IsManagementStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and user.is_platform_staff
            and hasattr(user, "staff_profile")
            and user.staff_profile.department == "management"
        )
