from django.contrib import admin
from .models.product import Product
from .models.category import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'price', 'stock_quantity', 'is_approved', 'is_active']
    list_filter = ['is_approved', 'is_active', 'created_at']
    search_fields = ['name', 'store__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['approved_at']
