import re

from django.db import migrations, models


def backfill_invoice_document_fields(apps, schema_editor):
    Invoice = apps.get_model('billing', 'Invoice')

    for invoice in Invoice.objects.all().order_by('id'):
        number = (invoice.invoice_number or '').strip().upper()
        document_type = 'BUDGET'
        sequence = 1

        match = re.match(r'^(PRE|FAC)-(\d{4})-(\d+)$', number)
        if match:
            document_type = 'BUDGET' if match.group(1) == 'PRE' else 'INVOICE'
            sequence = int(match.group(3))
        elif number.startswith('FAC-'):
            document_type = 'INVOICE'
            sequence = int(number.split('-')[-1]) if number.split('-')[-1].isdigit() else 1
        elif number.startswith('PRE-'):
            document_type = 'BUDGET'
            sequence = int(number.split('-')[-1]) if number.split('-')[-1].isdigit() else 1

        invoice.document_type = document_type
        invoice.document_sequence = sequence
        invoice.save(update_fields=['document_type', 'document_sequence', 'invoice_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_alter_supplier_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='document_type',
            field=models.CharField(choices=[('BUDGET', 'Presupuesto'), ('INVOICE', 'Factura')], default='BUDGET', max_length=20, verbose_name='Tipo de documento'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='document_sequence',
            field=models.PositiveIntegerField(default=1, editable=False),
        ),
        migrations.RunPython(backfill_invoice_document_fields, migrations.RunPython.noop),
    ]
