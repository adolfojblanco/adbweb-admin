from rest_framework import serializers

from apps.accounts.models import CustomerUser
from apps.billing.models import Supplier, Invoice, InvoiceLine, PaymentMethod
from apps.catalogs.models import Product


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceLineSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InvoiceLine
        fields = [
            'id',
            'product',
            'product_name',
            'description',
            'quantity',
            'unit_price',
            'tax_percentage',
            'line_subtotal',
            'tax_amount',
            'line_total',
        ]
        read_only_fields = ['line_subtotal', 'tax_amount', 'line_total']


class InvoiceSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all())
    customer_name = serializers.CharField(source='customer.billing_name', read_only=True)
    customer_tax_id = serializers.CharField(source='customer.tax_id', read_only=True)
    lines = InvoiceLineSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'document_type',
            'document_sequence',
            'customer',
            'customer_name',
            'customer_tax_id',
            'issue_date',
            'due_date',
            'status',
            'notes',
            'subtotal',
            'tax_total',
            'total',
            'lines',
        ]
        read_only_fields = ['id', 'invoice_number', 'document_sequence', 'subtotal', 'tax_total', 'total']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        invoice = Invoice.objects.create(**validated_data)

        for line_data in lines_data:
            InvoiceLine.objects.create(invoice=invoice, **line_data)

        invoice.recalculate_totals()
        return invoice

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if lines_data is not None:
            instance.lines.all().delete()
            for line_data in lines_data:
                InvoiceLine.objects.create(invoice=instance, **line_data)
            instance.recalculate_totals()

        return instance
