from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsOrderOwner, IsOrderSeller, CanUpdateOrderStatus

@extend_schema(tags=['Orders'])
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing orders.
    """
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action in ['update', 'partial_update', 'update_status']:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        
        if user.is_staff:
            return Order.objects.all()
        
        if hasattr(user, 'seller_profile'):
            # Orders containing items from this seller's store
            return Order.objects.filter(items__store__seller=user.seller_profile).distinct()
        
        # Regular customer: only their own orders
        return Order.objects.filter(user=user)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [CanUpdateOrderStatus()]
        if self.action == 'update_status':
            return [CanUpdateOrderStatus()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Cancel order",
        description="Cancel an order if it is still pending. Only the order owner can do this.",
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Order cannot be cancelled"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'You do not own this order'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status != Order.Status.PENDING:
            return Response({'error': 'Only pending orders can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            order.status = Order.Status.CANCELLED
            order.save()
            
            # Restore stock
            for item in order.items.all():
                product = item.product
                product.stock_quantity += item.quantity
                product.save()
                
        return Response(OrderSerializer(order).data)

    @extend_schema(
        summary="Update order status",
        description="Update the status of an order. Only staff or the involved seller can perform this.",
        request=OrderStatusUpdateSerializer,
        responses={
            200: OrderSerializer,
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Order not found")
        }
    )
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)
