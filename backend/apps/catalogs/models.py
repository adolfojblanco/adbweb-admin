from django.db import models

from apps.core.models import TimeStampedModel


# Create your models here.

# Tax Model
class Tax(TimeStampedModel):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(decimal_places=2, max_digits=5)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"

    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"


# Category Model
class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"
        ordering = ['name']


# Product Model
class Product(TimeStampedModel):
    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name="products")
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Si no tiene SKU
        if is_new and not self.sku:
            prefix = self.name.strip()[:3].upper()  # Primeras 3 letras.
            sku = f"{prefix}-{self.id:03d}"  # Formato CAM-001
            self.sku = sku
            self.save(update_fields=['sku'])

    class Meta:
        verbose_name_plural = "Productos"
        verbose_name = "Producto"

    def __str__(self):
        return f"{self.sku} - {self.name}"
