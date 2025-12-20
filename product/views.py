from django.db import models
from rest_framework import viewsets, permissions, status, serializers as drf_serializers
from rest_framework.response import Response
from .models.product import Product
from .models.category import Category
from .serializers import ProductSerializer, CategorySerializer
from .permissions import IsStoreOwnerForProduct
from store.models.store import Store

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Product.objects.all()
        
        # If user is a seller, show them their own products (even unapproved) + other approved products
        if user.is_authenticated and hasattr(user, 'seller_profile'):
            return Product.objects.filter(
                models.Q(store__seller=user.seller_profile) | models.Q(is_approved=True)
            )

        # General public sees only approved products from active stores
        return Product.objects.filter(is_approved=True, store__is_active=True, store__is_approved=True)

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsStoreOwnerForProduct()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Determine the store. For now, assume store is passed in request data.
        store_id = self.request.data.get('store')
        if not store_id:
            raise drf_serializers.ValidationError({"store": "Store ID is required."})
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise drf_serializers.ValidationError({"store": "Store not found."})

        # Check ownership
        if store.seller.user != self.request.user:
            raise drf_serializers.PermissionDenied("You do not own this store.")
        
        # Check if store is approved and active
        if not store.is_approved:
            raise drf_serializers.ValidationError({"store": "This store is not approved yet."})
        
        if store.is_suspended:
            raise drf_serializers.ValidationError({"store": "This store is suspended."})

        serializer.save(store=store)
