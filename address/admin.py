from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Address

class AddressInline(GenericTabularInline):
     model = Address
     extra = 1