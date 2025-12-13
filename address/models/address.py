from django.db import models
from django.conf import settings


class Address(models.Model):
    class Type(models.TextChoices):
        HOME = "home", "Home"
        WORK = "work", "Work"
        STORE = "store", "Store"
        WAREHOUSE = "warehouse", "Warehouse"
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    type = models.CharField(max_length=20, choices=Type.choices)
    
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)