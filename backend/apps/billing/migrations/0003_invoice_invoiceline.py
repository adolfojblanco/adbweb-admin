from decimal import Decimal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0005_customeruser_city_customeruser_postal_code_and_more'),
        ('catalogs', '0007_remove_tax_created_by_remove_tax_updated_by_and_more'),
        ('billing', '0002_rename_email_company_supplier_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('invoice_number', models.CharField(blank=True, default='', editable=False, max_length=20, unique=True)),
                ('issue_date', models.DateField(default=django.utils.timezone.localdate, verbose_name='Fecha de emisión')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha de vencimiento')),
                ('status', models.CharField(choices=[('DRAFT', 'Borrador'), ('ISSUED', 'Emitida'), ('PAID', 'Pagada'), ('CANCELLED', 'Cancelada')], default='DRAFT', max_length=20, verbose_name='Estado')),
                ('notes', models.TextField(blank=True, verbose_name='Observaciones')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('tax_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoices', to='accounts.customeruser', verbose_name='Cliente')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Factura',
                'verbose_name_plural': 'Facturas',
                'ordering': ['-issue_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255, verbose_name='Descripción')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Cantidad')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Precio unitario')),
                ('tax_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='IVA %')),
                ('line_subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('line_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='billing.invoice', verbose_name='Factura')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_lines', to='catalogs.product', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Línea de factura',
                'verbose_name_plural': 'Líneas de factura',
            },
        ),
    ]
