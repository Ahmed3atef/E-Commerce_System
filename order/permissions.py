from rest_framework import permissions

class IsOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsOrderSeller(permissions.BasePermission):
    """
    Check if the user is a seller who has a product in this order.
    """
    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user, 'seller_profile'):
            return False
        return obj.items.filter(store__seller=request.user.seller_profile).exists()

class CanUpdateOrderStatus(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Staff can update any order
        if request.user.is_staff:
            return True
        # Sellers can update order if it only contains products from their store?
        # A more robust way is per-item status, but let's allow sellers to see/update 
        # orders with their products for now as a common multi-vendor approach.
        if hasattr(request.user, 'seller_profile'):
             return obj.items.filter(store__seller=request.user.seller_profile).exists()
        return False
