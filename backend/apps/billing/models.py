from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.db.models import Max
from django.utils import timezone

from apps.accounts.models import CustomerUser
from apps.catalogs.models import Product
from apps.core.models import TimeStampedModel

# Billing models here.


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Proveedor", unique=True)
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(max_length=200, verbose_name="Email")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Suplidor"
        verbose_name_plural = "Suplidores"


class Invoice(TimeStampedModel):
    class DocumentType(models.TextChoices):
        BUDGET = 'BUDGET', 'Presupuesto'
        INVOICE = 'INVOICE', 'Factura'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        ISSUED = 'ISSUED', 'Emitida'
        PAID = 'PAID', 'Pagada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.BUDGET, verbose_name='Tipo de documento')
    document_sequence = models.PositiveIntegerField(default=1, editable=False)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True, default='', editable=False)
    customer = models.ForeignKey(CustomerUser, on_delete=models.PROTECT, related_name='invoices', verbose_name='Cliente')
    issue_date = models.DateField(default=timezone.localdate, verbose_name='Fecha de emisión')
    due_date = models.DateField(blank=True, null=True, verbose_name='Fecha de vencimiento')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Estado')
    notes = models.TextField(blank=True, verbose_name='Observaciones')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-issue_date', '-id']

    def __str__(self):
        number = self.invoice_number or f'#{self.pk or "nuevo"}'
        return f'{number} - {self.customer.billing_name}'

    def get_number_prefix(self):
        return 'PRE' if self.document_type == self.DocumentType.BUDGET else 'FAC'

    def get_number_period(self):
        return self.issue_date.strftime('%d%m')

    def build_invoice_number(self):
        return f'{self.get_number_prefix()}-{self.get_number_period()}-{self.document_sequence:02d}'

    def assign_sequence(self):
        max_sequence = (
            Invoice.objects.filter(
                document_type=self.document_type,
                issue_date=self.issue_date,
            ).aggregate(max_sequence=Max('document_sequence'))['max_sequence']
            or 0
        )
        self.document_sequence = max_sequence + 1

    def save(self, *args, **kwargs):
        creating = self._state.adding

        if creating:
            self.assign_sequence()
        else:
            previous = Invoice.objects.filter(pk=self.pk).values('document_type', 'document_sequence', 'issue_date').first()
            if previous:
                target_number = self.build_invoice_number()
                if self.document_type != previous['document_type'] or self.issue_date != previous['issue_date']:
                    if Invoice.objects.filter(invoice_number=target_number).exclude(pk=self.pk).exists():
                        self.assign_sequence()

        self.invoice_number = self.build_invoice_number()
        super().save(*args, **kwargs)

    def recalculate_totals(self, save=True):
        subtotal = Decimal('0.00')
        tax_total = Decimal('0.00')
        total = Decimal('0.00')

        for line in self.lines.all():
            subtotal += line.line_subtotal
            tax_total += line.tax_amount
            total += line.line_total

        self.subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.tax_total = tax_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if save and self.pk:
            super().save(update_fields=['subtotal', 'tax_total', 'total'])


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines', verbose_name='Factura')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='invoice_lines', verbose_name='Producto', blank=True, null=True)
    description = models.CharField(max_length=255, verbose_name='Descripción', blank=True, default='')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio unitario', blank=True, null=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='IVA %', blank=True, null=True)
    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Línea de factura'
        verbose_name_plural = 'Líneas de factura'

    def __str__(self):
        return f'{self.description} x {self.quantity}'

    def save(self, *args, **kwargs):
        if self.product and not self.description:
            self.description = self.product.name

        if self.product and self.unit_price in (None, ''):
            self.unit_price = self.product.sale_price

        if self.product and self.tax_percentage in (None, '') and getattr(self.product, 'tax', None):
            self.tax_percentage = self.product.tax.percentage

        unit_price = Decimal(self.unit_price or 0)
        tax_percentage = Decimal(self.tax_percentage or 0)
        subtotal = (Decimal(self.quantity) * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tax_amount = (subtotal * tax_percentage / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.line_subtotal = subtotal
        self.tax_amount = tax_amount
        self.line_total = (subtotal + tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)



class PaymentMethod(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Metodo de Pago", unique=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.title()
            super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Métodos de Pago"
        verbose_name_plural = "Métodos de Pagos"
    
    
    
