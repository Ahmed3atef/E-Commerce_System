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
    
    class Meta:
        model = Product
        fields = [
            'id', 'store', 'store_name', 'category', 'category_name', 
            'name', 'slug', 'description', 'price', 'compare_at_price', 
            'stock_quantity', 'is_active', 'is_approved', 'created_at', 'update_at'
        ]
        read_only_fields = ['slug', 'is_approved', 'store']

    def validate(self, attrs):
        user = self.context['request'].user
        # Store is validated in perform_create of the viewset usually
        return attrs
