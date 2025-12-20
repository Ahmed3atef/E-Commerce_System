from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models.store import Store
from .serializers import StoreSerializer, StoreApprovalSerializer
from .permissions import IsStoreOwner, IsStaffUser

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
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

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        store = self.get_object()
        store.is_approved = True
        store.approved_at = timezone.now()
        store.rejection_reason = ""
        store.save()
        return Response({'status': 'store approved'}, status=status.HTTP_200_OK)

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
