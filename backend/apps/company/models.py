from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import models

from apps.core.models import TimeStampedModel

def force_logo_name(instance, filename):
    # Sin importar cómo se llame el archivo que suba el usuario (ej: 'mi_gato.jpg'),
    # forzamos a que se guarde como 'logo.png'
    return 'logo.png'

class Company(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    email_company = models.EmailField(max_length=200, verbose_name="Email")
    phone = models.CharField(max_length=200, verbose_name="Teléfono")
    address = models.CharField(max_length=200, verbose_name="Dirección")
    website = models.URLField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)

    logo = models.ImageField(
        storage=staticfiles_storage,  # Guardar en static/img en lugar de media/
        upload_to=force_logo_name,  # Llamarlo SIEMPRE 'logo.png'
        null=True,
        blank=True,
        verbose_name="Logo Principal (Sobrescribe static/img/logo.png)"
    )