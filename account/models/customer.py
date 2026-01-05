from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from address.models import Address

User = settings.AUTH_USER_MODEL

# related models to customer:
# - address by generic foreign key

class CustomerProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="customer_profile")
    avatar = models.ImageField(upload_to="customer/avatar", blank=True, null=True)
    
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)

    address = GenericRelation(Address, related_query_name="customer_profile")

    preferred_language = models.CharField(max_length=10, default="en")
    marketing_opt_in = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CustomerProfile({self.user})"