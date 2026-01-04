from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product
from address.models import Address
from django.db import transaction

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'store', 'store_name']
        read_only_fields = ['price', 'store']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'order_number', 'status', 
            'payment_status', 'subtotal', 'discount_amount', 'total_amount', 
            'coupon', 'shipping_address', 'billing_address', 'items', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'user', 'subtotal', 'discount_amount', 'total_amount']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        min_length=1
    )

    coupon_code = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'shipping_address', 'billing_address', 'items', 'coupon_code']

    def validate_items(self, items):
        for item in items:
            if 'product' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Each item must have a product ID and quantity.")
            
            try:
                product = Product.objects.get(id=item['product'], is_active=True, is_approved=True)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item['product']} not found or not available.")
            
            if product.stock_quantity < item['quantity']:
                raise serializers.ValidationError(f"Not enough stock for product {product.name}.")
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        coupon_code = validated_data.pop('coupon_code', None)
        user = self.context['request'].user
        
        # Initial creation
        order = Order.objects.create(user=user, **validated_data)
        
        subtotal = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product'])
            quantity = item_data['quantity']
            # Important: price should be the discounted price if any automatic discount exists
            price = product.get_discounted_price()
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
                store=product.store
            )
            
            # Reduce stock
            product.stock_quantity -= quantity
            product.save()
            
            subtotal += price * quantity
        
        order.subtotal = subtotal
        
        # Handle Coupon
        discount_amount = 0
        if coupon_code:
            from discount.models import Coupon
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid and subtotal >= coupon.min_purchase_amount:
                     discount_amount = coupon.calculate_discount(subtotal)
                     order.coupon = coupon
                     coupon.used_count += 1
                     coupon.save()
            except Coupon.DoesNotExist:
                pass # Or raise error if you want strict validation
        
        order.discount_amount = discount_amount
        order.total_amount = subtotal - discount_amount
        order.save()
        return order

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
