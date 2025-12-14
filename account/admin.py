from django.contrib import admin
from .models import *

admin.site.register(customer.CustomerProfile)
admin.site.register(seller.SellerProfile)
admin.site.register(staff.StaffProfile)