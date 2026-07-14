from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel, Tax

# Catalogs models here.

# Category Model
class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"
        ordering = ['name']


# Product Model
class Product(TimeStampedModel):
    sku = models.CharField(max_length=32, unique=True, blank=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name="products")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.name = self.name.title()

        # Si no tiene id es nuevo
        if not self.pk:
            super().save(*args, **kwargs)

        # Si no tiene SKU
        if not self.sku:
            prefix = self.name.strip()[:3].upper()  # Primeras 3 letras.
            self.sku = f"{prefix}-{self.id:03d}"  # Formato CAM-001
            self.save(update_fields=['sku'])
        else:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Productos"
        verbose_name = "Producto"

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Service(models.Model):
    """Catálogo maestro de servicios (ej: Hosting, Consultoría)"""
    name = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Base")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=21, verbose_name="IVA %")
    is_active = models.BooleanField(default=True, verbose_name="¿Activo?")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return f"{self.name} ({self.base_price}€)"
