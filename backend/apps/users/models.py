from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManager

# Models for users.

class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'ADMIN'
    VENDEDOR = 'VENDEDOR'
    CLIENTE = 'CLIENTE'

    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (VENDEDOR, 'Vendedor'),
        (CLIENTE, 'Cliente'),
    ]
    username = models.CharField(max_length=20, unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CLIENTE)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.role})"

