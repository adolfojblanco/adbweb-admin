from django.db import models
from django.db.models import Sum

from apps.company.models import Company
from apps.accounts.models import CustomerUser
from apps.catalogs.models import Tax, Product
from apps.core.models import TimeStampedModel
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver



# Modelos de facturación

class Supplier(TimeStampedModel):
    """Modelo Suplidor"""
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, verbose_name="Nombre")
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Correo")

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Suplidores"
        verbose_name = "Suplidor"

    def __str__(self):
        return self.name


class PaymentMethod(TimeStampedModel):
    """Metodos de pago"""
    name = models.CharField(max_length=100, verbose_name="Metodo de Pago")

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-name']
        verbose_name_plural = "Métodos de pago"
        verbose_name = "Método de pago"

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
    issue_date = models.DateField(default=timezone.now, verbose_name="Fecha de Factura")
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
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name='taxes')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def _generate_correlative_number(self):
        """
        CORRECCIÓN 2: Genera un número correlativo secuencial real en lugar de usar el PK.
        Busca la última factura del año y le suma 1 para evitar saltos contables.
        """
        prefix = "FAC" if self.document_type == self.DocumentType.INVOICE else "PRE"
        year = self.issue_date.year if self.issue_date else timezone.now().year

        last_invoice = Invoice.objects.filter(
            document_type=self.document_type,
            issue_date__year=year
        ).order_by('-number').first()

        if last_invoice and last_invoice.number:
            try:
                # Si la última fue 'FAC-2026-0015', extraemos el '15' y le sumamos 1
                last_sequence = int(last_invoice.number.split('-')[-1])
                new_sequence = last_sequence + 1
            except ValueError:
                new_sequence = 1
        else:
            new_sequence = 1

        return f"{prefix}-{year}-{new_sequence:04d}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if is_new and not self.number:
            self.number = self._generate_correlative_number()
        elif not is_new:
            # Si se edita la factura para convertir un Presupuesto en Factura (o viceversa)
            try:
                old_instance = Invoice.objects.only('document_type').get(pk=self.pk)
                if old_instance.document_type != self.document_type:
                    self.number = self._generate_correlative_number()
            except Invoice.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def update_totals(self):
        """Calculo de factura"""
        items_sum = self.items.aggregate(total_sum=Sum('subtotal'))['total_sum']
        self.subtotal = items_sum or Decimal('0.00')

        # Calculamos los impuestos
        tax_percentage = self.tax.percentage if self.tax else Decimal('0.00')
        self.tax_amount = self.subtotal * (tax_percentage / Decimal('100'))

        self.total = self.subtotal + self.tax_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total'])

    def __str__(self):
        return f"{self.get_document_type_display()} {self.number}"


class InvoiceItem(TimeStampedModel):
    """Detalle de factura"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name="Factura")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='Producto')

    product_name = models.CharField(max_length=200, verbose_name="Nombre del producto", blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio Unitario")

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Descuento")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False,
                                   verbose_name="Subtotal Línea")

    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Facturas"

    def __str__(self):
        return f"{self.quantity}x {self.product_name} - Factura {self.invoice.id}"

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.unit_price:
                self.unit_price = self.product.price
            if not self.product_name:
                self.product_name = self.product.name

        # Calcular el subtotal de esta línea matemáticamente antes de guardarla
        # Convertimos quantity a Decimal para poder operarlo con los DecimalFields

        line_total = (self.unit_price * Decimal(self.quantity)) - self.discount
        self.subtotal = max(Decimal('0.00'), line_total)
        
        super().save(*args, **kwargs)


    @receiver(post_save, sender='billing.InvoiceItem')
    @receiver(post_delete, sender='billing.InvoiceItem')
    def update_invoice_totals_on_item_change(sender, instance, **kwargs):
        """
        Escucha la base de datos: Si alguien crea, edita o borra una línea de detalle (InvoiceItem),
        le avisa a la Factura (Invoice) que debe volver a hacer sus matemáticas.
        """
        if instance.invoice:
            instance.invoice.update_totals()

