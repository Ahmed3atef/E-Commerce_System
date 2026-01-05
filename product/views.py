from django.db import models
from django.utils import timezone
from rest_framework import viewsets, permissions, status, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models.product import Product
from .models.category import Category
from .serializers import ProductSerializer, CategorySerializer, ProductApprovalSerializer
from .permissions import IsStoreOwnerForProduct
from store.models.store import Store

@extend_schema(tags=['Categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing product categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

@extend_schema(tags=['Products'])
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing product instances.
    """
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
        if self.action in ['approve', 'reject']:
            return [permissions.IsAdminUser()]
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

    @extend_schema(
        summary="Approve a product",
        description="Approve a product for listing. Only staff users can perform this action.",
        request=None,
        responses={
            200: OpenApiResponse(description="Product approved successfully"),
            404: OpenApiResponse(description="Product not found"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        product = self.get_object()
        product.is_approved = True
        product.approved_at = timezone.now()
        product.rejection_reason = ""
        product.save()
        return Response({'status': 'product approved'}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Reject a product",
        description="Reject a product listing with a reason. Only staff users can perform this action.",
        request=ProductApprovalSerializer,
        responses={
            200: OpenApiResponse(description="Product rejected successfully"),
            400: OpenApiResponse(description="Invalid data provided"),
            404: OpenApiResponse(description="Product not found"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        product = self.get_object()
        serializer = ProductApprovalSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        product.is_approved = False
        product.approved_at = None
        product.rejection_reason = serializer.validated_data.get('rejection_reason')
        product.save()
        return Response({'status': 'product rejected'}, status=status.HTTP_200_OK)
