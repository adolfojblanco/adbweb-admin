import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify


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

    customer = models.ForeignKey(
        "Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Cliente",
    )

    class Meta:
        verbose_name_plural = "Usuarios"
        verbose_name = "Usuario"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}"
        return f"{full_name or self.username} ({self.get_role_display()})"


# Customer model
class Customer(models.Model):

    class CustomerType(models.TextChoices):
        PERSON = "PERSON", "Autónomo / Particular"
        COMPANY = "COMPANY", "Empresa"

    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.PERSON,
        verbose_name="Tipo de cliente"
    )

    billing_name = models.CharField(
        max_length=255,
        verbose_name="Nombre Comercial o Razón Social"
    )

    tax_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="CIF / NIF / NIE"
    )

    address = models.CharField(
        max_length=255,
        verbose_name="Dirección"
    )

    city = models.CharField(
        max_length=100,
        verbose_name="Ciudad"
    )

    province = models.CharField(
        max_length=100,
        verbose_name="Provincia"
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Código Postal"
    )

    country = models.CharField(
        max_length=100,
        default="España",
        verbose_name="País"
    )

    contact_email = models.EmailField(
        verbose_name="Correo de facturación"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["billing_name"]

    def save(self, *args, **kwargs):

        self.contact_email = self.contact_email.lower().strip()

        self.billing_name = self.billing_name.strip()

        self.tax_id = self.tax_id.upper().replace(" ", "")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.billing_name