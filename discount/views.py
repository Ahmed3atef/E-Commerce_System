from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Coupon, ProductDiscount
from .serializers import CouponSerializer, ProductDiscountSerializer, CouponApplySerializer
from django.utils import timezone
from django.db import models
from .permissions import IsCouponOwnerOrStaff, IsVerifiedSeller

@extend_schema(tags=['Discounts'])
class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Coupon.objects.none()
        if user.is_staff:
            return Coupon.objects.all()
        if hasattr(user, 'seller_profile'):
            return Coupon.objects.filter(models.Q(store__seller=user.seller_profile) | models.Q(store=None))
        
        return Coupon.objects.filter(is_active=True, store=None)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'apply']:
            return [permissions.IsAuthenticated()]
        if self.action == 'create':
            return [IsVerifiedSeller()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsCouponOwnerOrStaff()]
        return [permissions.IsAdminUser()]

    @extend_schema(
        summary="Validate and apply coupon",
        request=CouponApplySerializer,
        responses={200: OpenApiResponse(description="Coupon valid"), 400: OpenApiResponse(description="Invalid coupon")}
    )
    @action(detail=False, methods=['post'])
    def apply(self, request):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        amount = serializer.validated_data['order_amount']
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({'error': 'Coupon not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not coupon.is_valid:
            return Response({'error': 'Coupon is inactive or expired'}, status=status.HTTP_400_BAD_REQUEST)
            
        if amount < coupon.min_purchase_amount:
             return Response({'error': f'Minimum purchase amount of {coupon.min_purchase_amount} required'}, status=status.HTTP_400_BAD_REQUEST)
             
        discount_amount = coupon.calculate_discount(amount)
        
        return Response({
            'code': coupon.code,
            'discount_amount': discount_amount,
            'new_total': amount - discount_amount
        })

@extend_schema(tags=['Discounts'])
class ProductDiscountViewSet(viewsets.ModelViewSet):
    queryset = ProductDiscount.objects.all()
    serializer_class = ProductDiscountSerializer
    permission_classes = [permissions.IsAdminUser] # For now
