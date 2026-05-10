from django.contrib import admin
from .models import  PaymentMethod, Invoice


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # 1. Lista General: Añadimos colores y el saldo pendiente
    list_display = ('number', 'customer', 'document_type', 'total', 'subtotal', 'tax_amount')
    list_filter = ('document_type', 'status', 'issue_date')
    readonly_fields = ('number', 'total', 'tax_amount')
    search_fields = ('number', 'customer__billing_name', 'customer__tax_id')
