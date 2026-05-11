from django.db import models

from apps.core.models import TimeStampedModel


# Supplier models here.

class Supplier(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=9)
    email = models.EmailField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name