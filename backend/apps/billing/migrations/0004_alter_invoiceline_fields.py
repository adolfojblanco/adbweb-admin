from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_invoice_invoiceline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceline',
            name='description',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='tax_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, null=True, verbose_name='IVA %'),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='unit_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Precio unitario'),
        ),
    ]
