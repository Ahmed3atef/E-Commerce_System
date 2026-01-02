from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models.store import Store
from .serializers import StoreSerializer, StoreApprovalSerializer
from .permissions import IsStoreOwner, IsStaffUser

@extend_schema(tags=['Stores'])
class StoreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing store instances.
    """
    queryset = Store.objects.all()
    # update this to hide sensitive info from be in get request 
    serializer_class = StoreSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [(IsStoreOwner | IsStaffUser)()]
        if self.action in ['approve', 'reject']:
            return [IsStaffUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller_profile)

    @extend_schema(
        summary="Approve a store",
        description="Approve a store registration request. Only staff users can perform this action.",
        request=None,
        responses={
            200: OpenApiResponse(description="Store approved successfully"),
            404: OpenApiResponse(description="Store not found"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        store = self.get_object()
        store.is_approved = True
        store.approved_at = timezone.now()
        store.rejection_reason = ""
        store.save()
        return Response({'status': 'store approved'}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Reject a store",
        description="Reject a store registration request with a reason. Only staff users can perform this action.",
        request=StoreApprovalSerializer,
        responses={
            200: OpenApiResponse(description="Store rejected successfully"),
            400: OpenApiResponse(description="Invalid data provided"),
            404: OpenApiResponse(description="Store not found"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        store = self.get_object()
        serializer = StoreApprovalSerializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        store.is_approved = False
        store.approved_at = None
        store.rejection_reason = serializer.validated_data.get('rejection_reason')
        store.save()
        return Response({'status': 'store rejected'}, status=status.HTTP_200_OK)
