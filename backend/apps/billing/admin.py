from django.contrib import admin
from .models import PaymentMethod, Invoice, Supplier


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'document_type', 'total', 'subtotal', 'tax_amount')
    list_filter = ('document_type', 'status', 'issue_date')
    readonly_fields = ('number', 'total', 'tax_amount')
    search_fields = ('number', 'customer__billing_name', 'customer__tax_id')


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active')
    readonly_fields = ('created_by', 'updated_by',)
    search_fields = ('name', 'phone')

    def save_model(self, request, obj, form, change):
        # Si el objeto no tiene ID en la base de datos (change es False), es una CREACIÓN
        if not change:
            obj.created_by = request.user

        # Sin importar si es creación o edición, SIEMPRE actualizamos el updated_by
        obj.updated_by = request.user

        # Llamar al save_model original para que continúe su curso y guarde
        super().save_model(request, obj, form, change)

