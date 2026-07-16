from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from apps.billing.models import Invoice, InvoiceLine, Supplier, PaymentMethod


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    ordering = ('name',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    autocomplete_fields = ('product',)
    readonly_fields = ('line_subtotal', 'tax_amount', 'line_total')


class DocumentTypeFilter(admin.SimpleListFilter):
    title = 'Tipo de documento'
    parameter_name = 'document_type'

    def lookups(self, request, model_admin):
        return (
            ('BUDGET', 'Presupuestos'),
            ('INVOICE', 'Facturas'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(document_type=self.value())
        return queryset


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    change_form_template = 'admin/billing/invoice/change_form.html'
    list_display = ('invoice_number', 'document_type_badge', 'customer', 'issue_date', 'due_date', 'status', 'total')
    list_filter = (DocumentTypeFilter, 'status', 'issue_date')
    search_fields = ('invoice_number', 'customer__billing_name', 'customer__tax_id', 'customer__contact_email')
    autocomplete_fields = ('customer',)
    readonly_fields = ('invoice_number', 'document_sequence', 'subtotal', 'tax_total', 'total', 'created_at', 'updated_at')
    inlines = [InvoiceLineInline]
    ordering = ('-issue_date', '-id')
    actions = ['convert_selected_to_invoice']

    fieldsets = (
        ('Datos de factura', {
            'fields': ('invoice_number', 'document_type', 'document_sequence', 'customer', 'issue_date', 'due_date', 'status', 'notes')
        }),
        ('Totales', {
            'fields': ('subtotal', 'tax_total', 'total')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_totals()

    @admin.display(description='Tipo', ordering='document_type')
    def document_type_badge(self, obj):
        if obj.document_type == obj.DocumentType.INVOICE:
            return mark_safe(
                '<span style="padding:2px 8px;border-radius:999px;background:#0d6efd;color:white;font-size:12px;">Factura</span>'
            )

        return mark_safe(
            '<span style="padding:2px 8px;border-radius:999px;background:#6c757d;color:white;font-size:12px;">Presupuesto</span>'
        )

    @admin.action(description='Convertir presupuestos a factura')
    def convert_selected_to_invoice(self, request, queryset):
        converted = 0

        for invoice in queryset:
            if invoice.document_type != invoice.DocumentType.INVOICE:
                invoice.document_type = invoice.DocumentType.INVOICE
                invoice.save()
                converted += 1

        self.message_user(request, f'{converted} documento(s) convertidos a factura.')

    def response_change(self, request, obj):
        if '_convert_to_invoice' in request.POST and obj.document_type != obj.DocumentType.INVOICE:
            obj.document_type = obj.DocumentType.INVOICE
            obj.save()
            self.message_user(request, 'Documento convertido a factura correctamente.')
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)
