from rest_framework import serializers
from .models.product import Product
from .models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'icon', 'image']

class ProductSerializer(serializers.ModelSerializer):
    store_name = serializers.ReadOnlyField(source='store.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    
    current_price = serializers.SerializerMethodField()
    discount_info = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'store', 'store_name', 'category', 'category_name', 
            'name', 'slug', 'description', 'price', 'compare_at_price', 
            'current_price', 'discount_info',
            'stock_quantity', 'is_active', 'is_approved', 'approved_at', 
            'rejection_reason', 'created_at', 'update_at'
        ]
        read_only_fields = ['slug', 'is_approved', 'approved_at', 'rejection_reason', 'store']

    def get_current_price(self, obj):
        return obj.get_discounted_price()

    def get_discount_info(self, obj):
        discount = obj.get_active_discount()
        if discount:
            return {
                "name": discount.name,
                "value": discount.value,
                "type": discount.discount_type
            }
        return None

    def validate(self, attrs):
        # Store is validated in perform_create of the viewset usually
        return attrs

class ProductApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['is_approved', 'rejection_reason']

    def validate(self, attrs):
        if not attrs.get('is_approved') and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({"rejection_reason": "Required if rejecting the product."})
        return attrs
