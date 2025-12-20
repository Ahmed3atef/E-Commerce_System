from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    """
    parent field is category hierachical:
    Electronics
    ├── Mobiles
    │     ├── Android
    │     └── iPhone
    └── Laptops
    
    Electronics.parent = NULL
    Mobiles.parent = Electronics
    Android.parent = Mobiles
    
    Category.objects.filter(parent__isnull=True)
    category.children.all()
    """
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE
    )
    
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True) # for fontawesome etc
    image = models.ImageField(upload_to="category/images", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name