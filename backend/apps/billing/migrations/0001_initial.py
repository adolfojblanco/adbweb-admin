# Hand-authored equivalent of `python manage.py makemigrations billing` against the
# v2 schema currently defined in apps/billing/models.py.
#
# The previous migration history (0001-0009 and 0019) described a v1 schema
# (InvoiceLine, invoice_number, document_sequence, tax_total, line_subtotal,
# tax_amount, line_total, description, tax_percentage) that no longer matches
# the current Python models. That history was reset so the migration graph
# is linear and `manage.py check` succeeds.
#
# If you have a populated production database, run this against a fresh
# schema. There is no automatic data back-fill from v1 to v2.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0006_customer_remove_customeruser_user_alter_user_options_and_more'),
        ('catalogs', '0007_remove_tax_created_by_remove_tax_updated_by_and_more'),
        ('core', '0003_alter_tax_percentage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('phone', models.CharField(blank=True, max_length=11, null=True, verbose_name='Teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Correo')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Suplidor',
                'verbose_name_plural': 'Suplidores',
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100, verbose_name='Metodo de Pago')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Método de pago',
                'verbose_name_plural': 'Métodos de pago',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('document_type', models.CharField(choices=[('QUOTE', 'Presupuesto'), ('INVOICE', 'Factura')], default='QUOTE', max_length=10)),
                ('number', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='# Factura')),
                ('issue_date', models.DateField(default=django.utils.timezone.now, verbose_name='Fecha de Factura')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha de Pago')),
                ('status', models.CharField(choices=[('DRAFT', 'Borrador'), ('ISSUED', 'Emitida/Enviada'), ('ACCEPTED', 'Aceptada'), ('PAID', 'Pagada'), ('CANCELLED', 'Cancelada')], default='DRAFT', max_length=10)),
                ('notes', models.TextField(blank=True, help_text='Términos y condiciones o notas para el cliente')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.company', verbose_name='Empresa Emisora')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='invoices', to='accounts.customer')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='sales', to=settings.AUTH_USER_MODEL)),
                ('tax', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='taxes', to='core.tax')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Documento',
                'verbose_name_plural': 'Documentos',
                'ordering': ['-issue_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('product_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Nombre del producto')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Cantidad')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Precio Unitario')),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Descuento')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=12, verbose_name='Subtotal Línea')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='billing.invoice', verbose_name='Factura')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Producto', to='catalogs.product')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Detalle de Factura',
                'verbose_name_plural': 'Detalles de Facturas',
            },
        ),
    ]
