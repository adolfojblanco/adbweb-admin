from django.db import models

# Create your models for core.
class CustomModel(models.Model):
    created_at = models.DateTimeField(verbose_name="Creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Actualizado", auto_now=True)
    is_active = models.BooleanField(verbose_name="Activo", default=True)

    class Meta:
        abstract = True