from django.contrib import admin
from .models import Coupon, ProductDiscount

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'is_active', 'start_date', 'end_date', 'used_count']
    list_filter = ['is_active', 'discount_type', 'start_date']
    search_fields = ['code']
    readonly_fields = ['used_count']

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'value', 'is_active', 'start_date', 'end_date', 'priority']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['name']
    filter_horizontal = ['products', 'categories']
