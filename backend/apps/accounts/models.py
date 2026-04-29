from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SELLER = "SELLER", "Seller"
        CLIENT = "CLIENT", "Client"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT
    )

    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_admin(self):
        return self.role == self.role.ADMIN

    @property
    def is_seller(self):
        return self.role == self.role.SELLER

    def __str__(self):
        return f"{self.first_name} ({self.get_role_display()})"
