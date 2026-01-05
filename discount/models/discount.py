from django.db import models
from django.utils import timezone

class ProductDiscount(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED_AMOUNT = 'fixed', 'Fixed Amount'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    products = models.ManyToManyField('product.Product', related_name='discounts', blank=True)
    categories = models.ManyToManyField('product.Category', related_name='discounts', blank=True)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    # Priority if multiple discounts apply
    priority = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-priority', '-start_date']

    def __str__(self):
        return self.name

    @property
    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
