from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL

class SellerProfile(models.Model):
    class SellerType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        COMPANY = "company", "Company"
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="seller_profile")
    
    # Onboarding & verification
    seller_type = models.CharField(max_length=20, choices=SellerType.choices)
    is_verified = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)
    
    # Public-facing metadata
    display_name = models.CharField(max_length=255)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=20, blank=True)
    
     # Risk control
    is_suspended = models.BooleanField(default=False)
    suspended_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SellerProfile({self.display_name})"