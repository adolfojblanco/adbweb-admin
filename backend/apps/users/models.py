from tkinter.constants import CASCADE

from django.db import models
from apps.core.models import CustomModel
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
    first_name = models.CharField(verbose_name="Nombre", max_length=100, blank=False)
    last_name = models.CharField(verbose_name="Apellido", max_length=100, blank=False)
    username = models.CharField(verbose_name="Usuario", max_length=20, unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CLIENTE)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.role})"

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        super(User, self).save(*args, **kwargs)


    class Meta:
        verbose_name_plural = 'Usuarios'
        verbose_name = 'Usuaio'


class Client(CustomModel):
    mobile_phone = models.CharField(verbose_name='Móvil', max_length=9, null=False, blank=False)
    user = models.OneToOneField(User, verbose_name='Usuario', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.fist_name

    class Meta:
        verbose_name_plural = 'Clientes'
        verbose_name = 'Cliente'
