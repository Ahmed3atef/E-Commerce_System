from rest_framework import serializers

class SellerDashboardSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    
    order_status_distribution = serializers.DictField(child=serializers.IntegerField())
    low_stock_alerts = serializers.ListField(child=serializers.DictField())
    top_selling_products = serializers.ListField(child=serializers.DictField())
    daily_sales = serializers.ListField(child=serializers.DictField())
