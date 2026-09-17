from rest_framework import serializers

from apps.accounts.models import Customer
from apps.billing.models import Supplier, Invoice, InvoiceItem, PaymentMethod
from apps.catalogs.models import Product
from apps.core.models import Company, Tax


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'unit_price',
            'discount',
            'subtotal',
        ]
        read_only_fields = ['subtotal']


class InvoiceSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    customer_name = serializers.CharField(source='customer.billing_name', read_only=True)
    customer_tax_id = serializers.CharField(source='customer.tax_id', read_only=True)
    tax = serializers.PrimaryKeyRelatedField(queryset=Tax.objects.all())
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    items = InvoiceItemSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'number',
            'document_type',
            'customer',
            'customer_name',
            'customer_tax_id',
            'seller',
            'seller_name',
            'company',
            'tax',
            'issue_date',
            'due_date',
            'status',
            'notes',
            'subtotal',
            'tax_amount',
            'total',
            'items',
        ]
        read_only_fields = [
            'id',
            'number',
            'subtotal',
            'tax_amount',
            'total',
            'document_type',
            'seller',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['seller'] = request.user
        else:
            validated_data.setdefault('seller', request.user if request else None)

        if not validated_data.get('company'):
            company = Company.objects.first()
            if company:
                validated_data['company'] = company

        invoice = Invoice.objects.create(**validated_data)

        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        invoice.update_totals()
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        validated_data.pop('document_type', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)
            instance.update_totals()

        return instance
