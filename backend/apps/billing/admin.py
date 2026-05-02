from django.contrib import admin
from django.urls import path
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceItem, Payment
from .views import export_invoice_pdf


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit_price', 'tax_percentage', 'subtotal', 'total')
    readonly_fields = ('subtotal', 'total')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1  # Permite añadir el abono del 30% directamente
    fields = ('date', 'amount', 'method', 'reference')
    readonly_fields = ('date',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # 1. Lista General: Añadimos colores y el saldo pendiente
    list_display = ('number', 'customer', 'document_type', 'status_color', 'total', 'display_pending', 'pdf_button')
    list_filter = ('document_type', 'status', 'issue_date')
    search_fields = ('number', 'customer__billing_name', 'customer__tax_id')

    def pdf_button(self, obj):
        if obj.id:
            from django.urls import reverse
            try:
                # AQUÍ ESTÁ LA CLAVE: Tiene que decir 'billing:invoice_pdf_final'
                url = reverse('billing:invoice_pdf_final', args=[obj.id])
                return mark_safe(
                    f'<a class="button" style="background-color: #79aec8; color: white;" href="{url}" target="_blank">📄 PDF</a>')
            except Exception as e:
                return format_html('<span style="color:red; font-size:10px;">Error: {}</span>', str(e))
        return ""

    pdf_button.short_description = "Acciones"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:invoice_id>/pdf/',
                self.admin_site.admin_view(export_invoice_pdf),
                name='generar_factura_pdf_global',  # Un nombre único y manual
            ),
        ]
        return custom_urls + urls

    # 2. Formulario: Organizamos para ver cuánto se ha cobrado
    fieldsets = (
        ('Información Principal', {
            'fields': ('document_type', 'number', 'status', 'customer', 'seller')
        }),
        ('Fechas', {
            'fields': ('due_date',)
        }),
        ('Control de Cobro (Totales)', {
            'fields': (
                ('subtotal', 'tax_amount', 'total'), # Fila 1: Lo que se debe
                ('display_total_paid', 'display_pending'), # Fila 2: Lo que se ha pagado
            ),
            'description': 'Resumen financiero de la factura y sus abonos.'
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )

    # Definimos qué campos no se pueden tocar a mano
    readonly_fields = ('subtotal', 'tax_amount', 'total', 'number', 'display_total_paid', 'display_pending')

    # 3. Inlines: Primero los productos, luego los pagos
    inlines = [InvoiceItemInline, PaymentInline]

    # --- MÉTODOS DE FORMATO ---

    def display_total_paid(self, obj):
        return f"{obj.total_paid} €"
    display_total_paid.short_description = "Total Cobrado"

    def display_pending(self, obj):
        amount = obj.pending_amount
        color = "green" if amount <= 0 else "red"
        return format_html('<b style="color: {};">{} €</b>', color, amount)
    display_pending.short_description = "Pendiente de Cobro"

    def status_color(self, obj):
        colors = {
            'PAID': '#28a745',       # Verde
            'DRAFT': '#6c757d',      # Gris
            'CANCELLED': '#dc3545',  # Rojo
            'ISSUED': '#17a2b8',     # Cian
            'ACCEPTED': '#ffc107',   # Amarillo/Naranja
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#333'),
            obj.get_status_display()
        )
    status_color.short_description = "Estado"

