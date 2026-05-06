from django.db import models
from django.db.models import Sum

from apps.company.models import Company
from apps.accounts.models import CustomerUser
from apps.catalogs.models import Tax
from apps.core.models import TimeStampedModel
from django.conf import settings
import datetime



# Modelos de facturación

class PaymentMethod(TimeStampedModel):
    """Metodos de pago"""
    name = models.CharField(max_length=100, verbose_name="Metodo de Pago")

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-name']
        verbose_name_plural = "Metodos de pago"
        verbose_name = "Metodo de pago"

    def __str__(self):
        return self.name


class Invoice(TimeStampedModel):
    """Modelo de factura"""
    class DocumentType(models.TextChoices):
        QUOTE = "QUOTE", "Presupuesto"
        INVOICE = "INVOICE", "Factura"

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        ISSUED = 'ISSUED', 'Emitida/Enviada'
        ACCEPTED = 'ACCEPTED', 'Aceptada'
        PAID = 'PAID', 'Pagada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    # Datos principales
    document_type = models.CharField(max_length=10, choices=DocumentType.choices, default=DocumentType.QUOTE)
    number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="# Factura")
    issue_date = models.DateField(auto_now=True, verbose_name="Fecha de Factura")
    due_date = models.DateField(auto_now=False, verbose_name="Fecha de Pago")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True, help_text="Términos y condiciones o notas para el cliente")

    # Relaciones
    customer = models.ForeignKey(CustomerUser, on_delete=models.RESTRICT, related_name='invoices')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='sales')

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,  # PROTECT evita que borres una empresa si tiene facturas
        null=True,
        blank=True,
        verbose_name="Empresa Emisora"
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name='taxes')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        # Prefijo para factura o presupuesto
        prefix = "FAC" if self.document_type == self.DocumentType.INVOICE else "PRE"
        year = self.issue_date.year if self.issue_date else datetime.datetime.now().year
        if is_new:
            # Si es nuevo, primero guardamos para obtener el PK (ID)
            super().save(*args, **kwargs)
            # Generamos el número inicial (ej: PRE-2026-0005)
            self.number = f"{prefix}-{year}-{self.pk:04d}"
            # Actualizamos solo el campo number para evitar bucles
            Invoice.objects.filter(pk=self.pk).update(number=self.number)
        else:
            # 2. Si ya existe, comprobamos si el document_type ha cambiado en la BD
            old_instance = Invoice.objects.only('document_type').get(pk=self.pk)

            if old_instance.document_type != self.document_type:
                # Si cambió, reconstruimos el número con el nuevo prefijo pero MISMO PK
                self.number = f"{prefix}-{year}-{self.pk:04d}"

            self.tax_amount = (self.subtotal or 0.00) * (self.tax.percentage/100 or 0.00)
            self.total = (self.subtotal or 0.00) + (self.tax_amount or 0.00)

            super().save(*args, **kwargs)