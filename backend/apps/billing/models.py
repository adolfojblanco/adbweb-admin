
from apps.core.models import TimeStampedModel
from django.db import models

# Billing models here.


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Proveedor", unique=True)
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(max_length=200, verbose_name="Email")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.email_company = self.email.lower()
        super().save(*args, **kwargs)