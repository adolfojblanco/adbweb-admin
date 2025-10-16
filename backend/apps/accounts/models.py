from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SELLER = "SELLER", "Seller"
        CLIENT = "CLIENT", "Client"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
