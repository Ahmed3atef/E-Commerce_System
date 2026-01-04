from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED_AMOUNT = 'fixed', 'Fixed Amount'

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Validation rules
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Total number of times this coupon can be used")
    used_count = models.PositiveIntegerField(default=0)
    
    user_limit = models.PositiveIntegerField(default=1, help_text="Number of times a single user can use this coupon")
    
    is_active = models.BooleanField(default=True)
    
    # Store scoping (if a seller wants to create a coupon for their store only)
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, null=True, blank=True, related_name='coupons')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date > now or self.end_date < now:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, amount):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return (amount * self.value) / 100
        return min(self.value, amount)
