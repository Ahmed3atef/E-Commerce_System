from rest_framework import serializers
from .models import Coupon, ProductDiscount
from store.models.store import Store

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['used_count']

    def validate(self, attrs):
        if attrs.get('end_date') <= attrs.get('start_date', attrs.get('start_date')):
             raise serializers.ValidationError("End date must be after start date.")
        return attrs

class ProductDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = '__all__'

class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
