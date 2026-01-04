from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from order.models import Order, OrderItem
from product.models import Product
from store.models import Store
from .serializers import SellerDashboardSerializer

@extend_schema(tags=['Analytics'])
class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_seller_store(self, user):
        try:
            return Store.objects.get(seller__user=user)
        except Store.DoesNotExist:
            return None

    @extend_schema(
        summary="Get seller dashboard analytics",
        responses={200: SellerDashboardSerializer}
    )
    @action(detail=False, methods=['get'], url_path='seller-dashboard')
    def seller_dashboard(self, request):
        user = request.user
        store = self.get_seller_store(user)
        
        if not store:
            return Response({"error": "No store found for this seller"}, status=status.HTTP_404_NOT_FOUND)

        
        store_items = OrderItem.objects.filter(store=store)
        store_orders = Order.objects.filter(items__store=store).distinct()

        
        total_revenue = store_items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or Decimal('0.00')
        total_orders = store_orders.count()
        total_products = Product.objects.filter(store=store).count()
        total_customers = store_orders.values('user').distinct().count()

        
        status_dist = {}
        for s_code, s_name in Order.Status.choices:
            count = store_orders.filter(status=s_code).count()
            if count > 0:
                status_dist[s_name] = count

        
        low_stock = Product.objects.filter(store=store, stock_quantity__lt=5).values('id', 'name', 'stock_quantity')

        
        top_products = Product.objects.filter(store=store)\
            .annotate(units_sold=Sum('order_items__quantity'))\
            .filter(units_sold__gt=0)\
            .order_by('-units_sold')[:5]\
            .values('id', 'name', 'units_sold')

        
        last_7_days = []
        now = timezone.now()
        for i in range(6, -1, -1):
            date = (now - timedelta(days=i)).date()
            daily_rev = store_items.filter(order__created_at__date=date)\
                .aggregate(total=Sum(F('price') * F('quantity')))['total'] or Decimal('0.00')
            last_7_days.append({
                "date": date.strftime('%Y-%m-%d'),
                "revenue": daily_rev
            })

        data = {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_products": total_products,
            "total_customers": total_customers,
            "order_status_distribution": status_dist,
            "low_stock_alerts": list(low_stock),
            "top_selling_products": list(top_products),
            "daily_sales": last_7_days
        }

        return Response(data)
