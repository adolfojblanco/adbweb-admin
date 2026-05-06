import re
from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.models import TimeStampedModel
from apps.catalogs.models import Product
from apps.company.models import Company


# Modelos de facturación

class Invoice(TimeStampedModel):
    class DocumentType(models.TextChoices):
        QUOTE = 'QUOTE', 'Presupuesto'
        INVOICE = 'INVOICE', 'Factura'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        ISSUED = 'ISSUED', 'Emitida/Enviada'
        ACCEPTED = 'ACCEPTED', 'Aceptada'
        PAID = 'PAID', 'Pagada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    # Datos principales
    document_type = models.CharField(max_length=10, choices=DocumentType.choices, default=DocumentType.QUOTE)
    number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="# Factura")
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True, help_text="Términos y condiciones o notas para el cliente")

    # Relaciones
    customer = models.ForeignKey('accounts.CustomerUser', on_delete=models.RESTRICT, related_name='invoices')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='sales')
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,  # PROTECT evita que borres una empresa si tiene facturas
        null=True,
        blank=True,
        verbose_name="Empresa Emisora"
    )

    # Totales (Caché)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def total_paid(self):
        """Suma todos los pagos registrados para esta factura"""
        # Usamos el 'related_name=payments' que debe estar en el modelo Payment
        if not self.pk:  # Si la factura es nueva y no se ha guardado, el total pagado es 0
            return Decimal('0.00')
        return self.payments.aggregate(res=Sum('amount'))['res'] or Decimal('0.00')

    @property
    def pending_amount(self):
        """Calcula la deuda restante: Total Factura - Total Pagado"""
        return self.total - self.total_paid

    # --- MÉTODOS DE LÓGICA ---

    def update_totals(self):
        """Suma los items para actualizar el subtotal y total de la factura"""
        aggregates = self.items.aggregate(
            sum_subtotal=Sum('subtotal'),
            sum_total=Sum('total')
        )
        self.subtotal = aggregates['sum_subtotal'] or Decimal('0.00')
        self.total = aggregates['sum_total'] or Decimal('0.00')
        self.tax_amount = self.total - self.subtotal

        # Guardamos usando update para no disparar el save() de nuevo
        Invoice.objects.filter(pk=self.pk).update(
            subtotal=self.subtotal,
            tax_amount=self.tax_amount,
            total=self.total
        )

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        # 1. Definimos el prefijo según el tipo de documento actual
        prefix = "FAC" if self.document_type == self.DocumentType.INVOICE else "PRE"
        import datetime
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

        if not self.company_id:
            from apps.company.models import Company
            # buscamos la primera empresa que exista en la base de datos y se la asignamos
            primera_empresa = Company.objects.first()
            if primera_empresa:
                self.company = primera_empresa

            super().save(*args, **kwargs)

    def update_totals(self):
        """Calcula el total basado en todos los items"""
        aggregates = self.items.aggregate(
            resultado_subtotal=Sum('subtotal'),  # Usamos nombres claros
            resultado_total=Sum('total')
        )

        # Extraemos los resultados usando los nombres de arriba
        self.subtotal = aggregates['resultado_subtotal'] or Decimal('0.00')
        self.total = aggregates['resultado_total'] or Decimal('0.00')
        self.tax_amount = self.total - self.subtotal

        # Guardamos directamente en la base de datos para evitar conflictos
        Invoice.objects.filter(pk=self.pk).update(
            subtotal=self.subtotal,
            tax_amount=self.tax_amount,
            total=self.total
        )

    def __str__(self):
        return f"{self.get_document_type_display()} {self.number or 'S/N'}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, verbose_name="Producto")

    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")

    # Campos que se rellenan automáticamente del producto
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     verbose_name="Precio unitario")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         verbose_name="Impuesto %")

    # Totales de línea
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        # 1. Foto del momento: Si no hay datos, traerlos del producto
        if not self.unit_price and self.product:
            self.unit_price = self.product.sale_price

        if self.tax_percentage is None and self.product:
            # Traemos el impuesto del producto o el 21.00 por defecto si no tiene
            self.tax_percentage = getattr(self.product, 'tax_percentage', Decimal('21.00'))

        if not self.description and self.product:
            self.description = self.product.name

        price = self.unit_price or Decimal('0.00')
        tax = self.tax_percentage or Decimal('0.00')

        self.subtotal = price * self.quantity
        tax_amount = self.subtotal * (tax / Decimal('100.00'))
        self.total = self.subtotal + tax_amount

        super().save(*args, **kwargs)

        if self.invoice:
            self.invoice.update_totals()

    def __str__(self):
        return f"{self.quantity}x {self.description}"


class Payment(models.Model):
    class Method(models.TextChoices):
        TRANSFER = 'TRANSFER', 'Transferencia'
        CASH = 'CASH', 'Efectivo'
        CARD = 'CARD', 'Tarjeta'

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad Pagada")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Pago")
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.TRANSFER)
    reference = models.CharField(max_length=100, blank=True, help_text="Nº de transferencia o recibo")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Cada vez que se registra un pago, recalculamos la factura
        self.invoice.update_totals()

    def __str__(self):
        return f"{self.amount}€ - {self.get_method_display()}"


@receiver(post_save, sender=InvoiceItem)
def update_invoice_on_save(sender, instance, **kwargs):
    if instance.invoice:
        instance.invoice.update_totals()

@receiver(post_delete, sender=InvoiceItem)
def update_invoice_on_delete(sender, instance, **kwargs):
    if instance.invoice:
        instance.invoice.update_totals()



class PaymentMethod(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Metodo de Pago")

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


    class Meta:
        ordering = ['name']
        verbose_name_plural = "Metodos de pago"
        verbose_name = "Metodo de pago"

    def __str__(self):
        return self.name




