from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    username = None
    # define the users roles
    class Role(models.TextChoices):
        STAFF = "staff", "Staff"
        CUSTOMER = "customer", "Customer"
        SELLER = "seller", "Seller"
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[1-9]\d{7,14}$",
                message="Phone number must be in international format (e.g. +201234567890)"
            )
        ]
    )
    is_phone_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices = Role.choices,
        default=Role.CUSTOMER
        
    )

    # make email-based auth
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [] # username removed
    
    def __str__(self):
        return self.email