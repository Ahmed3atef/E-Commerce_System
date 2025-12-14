import uuid
from django.db import models
from django.utils.text import slugify
from account.models.seller import SellerProfile
from django.db import IntegrityError, transaction

class Store(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name="store")
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    description = models.TextField(blank=True)
    
    logo = models.ImageField(upload_to="store/logos", blank=True, null=True)
    banner = models.ImageField(upload_to="store/banners", blank=True, null=True)
    
    # Moderation
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Business rules
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # Risk control
    is_suspended = models.BooleanField(default=False)
    suspended_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            
            random_suffix = uuid.uuid4().hex[:8]
            self.slug = f"{base_slug}-{random_suffix}"
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError:
            random_suffix = uuid.uuid4().hex[:8]
            self.slug = f"{base_slug}-{random_suffix}"
            super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("seller", "name")

    def __str__(self):
        return self.name