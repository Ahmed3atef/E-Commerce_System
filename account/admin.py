# account/admin.py
from django.contrib import admin
from .models import CustomerProfile, SellerProfile, StaffProfile
from address.admin import AddressInline

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    inlines = [AddressInline]

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    inlines = [AddressInline]

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    inlines = [AddressInline]