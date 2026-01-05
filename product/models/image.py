from django.db import models



class ProductImage(models.Model):
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        related_name="images"
    )
    
    image = models.ImageField(
        upload_to = "product/images",
    )
    
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    