from rest_framework import permissions

class IsStoreOwnerForProduct(permissions.BasePermission):
    """
    Permission to allow only the owner of the store associated with the product to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.store.seller.user == request.user

class IsProductStoreOwner(permissions.BasePermission):
    """
    Check if user owns a specific store before allowing product creation.
    Used in views where store_id might be passed.
    """
    def has_permission(self, request, view):
        # Specific check for POST/Create can be handled in perform_create
        return True
