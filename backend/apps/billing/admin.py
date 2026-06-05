from django.contrib import admin
from .models import PaymentMethod, Invoice, Supplier, InvoiceItem


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active',)


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


# 1. El Inline: Permite editar los Ítems dentro de la vista de la Factura
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1  # Muestra 1 fila vacía por defecto para agregar un nuevo producto
    readonly_fields = ('subtotal',)  # Protegemos el subtotal de la línea

    # Ordenamos las columnas para que sea intuitivo como un Punto de Venta
    fields = ('product', 'product_name', 'quantity', 'unit_price', 'discount', 'subtotal')

    # Autocomplete para que buscar productos no colapse si tienes miles de registros
    autocomplete_fields = ['product']


# 2. El Admin Principal de la Factura
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # Qué columnas ver en la lista general
    list_display = ('number', 'document_type', 'customer', 'status', 'issue_date', 'total')

    # Filtros laterales muy útiles para contabilidad
    list_filter = ('status', 'document_type', 'issue_date', 'company')

    # Buscador (Ajusta 'customer__email' o 'customer__username' según tu modelo de usuario)
    search_fields = ('number', 'customer__username', 'customer__first_name')

    # Protegemos los campos autocalculados de la cabecera
    readonly_fields = ('number', 'subtotal', 'tax_amount', 'total')

    # Conectamos las líneas de detalle
    inlines = [InvoiceItemInline]

    # Optimizamos consultas a la base de datos (evita el problema N+1)
    select_related = ('customer', 'seller', 'company', 'tax')
    autocomplete_fields = ['customer', 'seller', 'company']

    # Agrupamos los campos en secciones elegantes en la vista de detalle
    fieldsets = (
        ('Información del Documento', {
            'fields': (
                ('document_type', 'number'),
                ('issue_date', 'due_date'),
                'status'
            )
        }),
        ('Partes Involucradas', {
            'fields': (
                ('company', 'tax'),
                ('customer', 'seller'),
            )
        }),
        ('Totales (Autocalculados por el sistema)', {
            'fields': (
                ('subtotal', 'tax_amount', 'total'),
            ),
            'classes': ('collapse',)  # Mantiene esta sección colapsada por defecto para limpiar la vista
        }),
        ('Información Adicional', {
            'fields': ('notes',)
        }),
    )
