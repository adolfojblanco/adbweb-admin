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

    verbose_name_plural = "Usuarios"
    verbose_name = "Usuario"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}"
        return f"{full_name or self.username} ({self.get_role_display()})"


# Customer model
class CustomerUser(models.Model):
    class CustomerType(models.TextChoices):
        PERSON = 'PERSON', 'Autónomo / Particular'
        COMPANY = 'COMPANY', 'Empresa'

    # Datos de Facturación
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices, default=CustomerType.PERSON)
    billing_name = models.CharField(max_length=255, verbose_name="Nombre Comercial o Razón Social")
    tax_id = models.CharField(max_length=50, verbose_name="CIF / NIF / NIE")
    address = models.TextField(verbose_name="Dirección de Facturación")

    # Datos de Contacto Directo
    contact_email = models.EmailField(verbose_name="Correo para envío de facturas")
    phone = models.CharField(verbose_name="Teléfono", max_length=20, blank=True, null=True)

    # Conexión con el Login (Opcional, porque puedes tener clientes sin acceso al panel aún)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profile',
        verbose_name="Usuario",
    )

    class Meta:
        verbose_name_plural = "Clientes"
        verbose_name = "Cliente"

    def save(self, *args, **kwargs):
        self.contact_email = self.contact_email.lower()
        name = self.billing_name.strip()
        if name.islower() or name.isupper():
            self.billing_name = name.title()
        else:
            self.billing_name = name

        self.tax_id = self.tax_id.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.billing_name} ({self.get_customer_type_display()})"


# Señal para automatizar la creación del usuario
@receiver(post_save, sender=CustomerUser)
def create_user_for_customer(sender, instance, created, **kwargs):
    # Solo actuamos si es un registro nuevo y no tiene usuario
    if created and not instance.user:
        # 1. Limpieza de nombre
        temp_slug = slugify(instance.billing_name).replace("-", "")
        # Quitamos terminaciones legales comunes
        clean_name = re.sub(r'(sl|sa|sas|asoc)$', '', temp_slug.lower())

        # Fallback por si el nombre queda vacío tras la limpieza
        username = clean_name or f"user_{instance.pk}"

        # 2. Control de duplicados (Bucle corregido)
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1  # ¡Importante!

        # 3. Creamos el usuario
        # Nota: CustomerUser no tiene first_name/last_name,
        # así que usamos billing_name para el perfil
        new_user = User.objects.create_user(
            username=username,
            email=instance.contact_email,
            password=instance.tax_id,  # Password inicial = DNI/CIF
            role=User.Role.CLIENT,
            first_name=instance.billing_name[:30]
        )
        # 4. Vinculación silenciosa
        # Usamos .update() para evitar que el signal se dispare a sí mismo (recursión)
        CustomerUser.objects.filter(pk=instance.pk).update(user=new_user)
