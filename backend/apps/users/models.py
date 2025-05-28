from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Comprador'),
        ('SELLER', 'Vendedor'),
        ('ADMIN', 'Administrador'),
    )
    role = models.CharField('Rol', choices=ROLE_CHOICES, blank=False, default='CUSTOMER', max_length=15)

    def __str__(self):
        return self.username

