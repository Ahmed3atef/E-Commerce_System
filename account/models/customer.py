from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL

class CustomerProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="customer_profile")
    
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)

    preferred_language = models.CharField(
        max_length=10,
        default="en"
    )

    marketing_opt_in = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CustomerProfile({self.user})"