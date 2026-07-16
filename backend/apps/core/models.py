from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


# Create your models here.

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


def force_logo_name(instance, filename):
    # Sin importar cómo se llame el archivo que suba el usuario (ej: 'mi_gato.jpg'),
    # forzamos a que se guarde como 'logo.png'
    return 'logo.png'

class Company(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    email_company = models.EmailField(max_length=200, verbose_name="Email")
    phone = models.CharField(max_length=200, verbose_name="Teléfono")
    website = models.URLField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, verbose_name="Dirección", blank=True, null=True)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    logo = models.ImageField(
        storage=staticfiles_storage,  # Guardar en static/img en lugar de media/
        upload_to=force_logo_name,  # Llamarlo SIEMPRE 'logo.png'
        null=True,
        blank=True,
        verbose_name="Logo Principal (Sobrescribe static/img/logo.png)"
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name

    def clean(self):
        if not self.pk and Company.objects.exists():
            raise ValidationError("Solo puede existir una empresa")

    def save(self, *args, **kwargs):
        self.full_clean()
        self.email_company = self.email_company.lower()
        return super(Company, self).save(*args, **kwargs)


# Tax Model
class Tax(TimeStampedModel):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(verbose_name="Porcentaje", decimal_places=2, max_digits=5)

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"



