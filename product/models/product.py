from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    store = models.ForeignKey("store.Store", on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey("product.Category", null=True, blank=True, on_delete=models.SET_NULL, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    
    description = models.TextField(blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    stock_quantity = models.PositiveIntegerField(default = 0)
    
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Inside the SAME store, two products cannot have the same slug But different stores CAN use the same slug
        constraints = [
            models.UniqueConstraint(
                fields = ["store", "slug"],
                name = "unique_product_slug_per_store"
            )
        ]
        ordering = ["-created_at"]
        
        
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name