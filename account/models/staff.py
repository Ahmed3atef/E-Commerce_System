from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL

class StaffProfile(models.Model):
    class Department(models.TextChoices):
        MANAGEMENT = "management", "Management"
        CUSTOMER_CARE = "customer_care", "Customer Care"
        DELIVERY = "delivery", "Delivery"
        OPERATIONAL = "operational", "Operational"
        
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="staff_profile")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.user.email} - {self.department}"


