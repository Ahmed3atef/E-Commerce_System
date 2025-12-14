from django.db import models
from django.conf import settings
import uuid


User = settings.AUTH_USER_MODEL

class StaffProfile(models.Model):
    class Department(models.TextChoices):
        MANAGEMENT = "management", "Management"
        CUSTOMER_CARE = "customer_care", "Customer Care"
        DELIVERY = "delivery", "Delivery"
        OPERATIONAL = "operational", "Operational"
        
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="staff_profile")
    # avatar = models.ImageField(upload_to="seller/avatar", blank=True, null=True)
    department = models.CharField(max_length=20, choices=Department.choices)
    job_title = models.CharField(max_length=100)
    employee_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_active_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.department}"


