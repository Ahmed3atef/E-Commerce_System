from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q
from django.db import models


class Address(models.Model):
    ALLOWED_MODELS = Q(app_label='account', model='customerprofile') | \
        Q(app_label='account', model='sellerprofile') | \
        Q(app_label='account', model='staffprofile')
    class Type(models.TextChoices):
        HOME = "home", "Home"
        WORK = "work", "Work"
        STORE = "store", "Store"
        WAREHOUSE = "warehouse", "Warehouse"
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=ALLOWED_MODELS, related_name="address")
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    
    type = models.CharField(max_length=20, choices=Type.choices)
    
    """
    TODO: you should make validation before add data to country field
    import pycountry

    def validate_country_code(self, value):
        if not pycountry.countries.get(alpha_2=value):
            raise serializers.ValidationError("Invalid country code")
        return value
        
    """
    country = models.CharField(max_length=2, help_text="ISO 3166-1 alpha-2 country code")
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.type.capitalize()} Address for {self.content_object}"
    
    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"