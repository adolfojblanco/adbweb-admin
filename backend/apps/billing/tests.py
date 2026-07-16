from datetime import date

from django.test import TestCase

from apps.accounts.models import CustomerUser
from apps.billing.models import Invoice, InvoiceLine
from apps.billing.serializers import InvoiceSerializer
from apps.catalogs.models import Category, Product
from apps.core.models import Tax
from rest_framework.test import APIClient
from apps.accounts.models import User


class InvoiceModelTests(TestCase):
    def setUp(self):
        self.customer = CustomerUser.objects.create(
            customer_type=CustomerUser.CustomerType.COMPANY,
            billing_name='Cliente Factura',
            tax_id='B12345678',
            address='Calle Factura 1',
            city='Madrid',
            province='Madrid',
            contact_email='factura@example.com',
        )
        self.tax = Tax.objects.create(name='IVA', percentage=21)
        self.category = Category.objects.create(name='Servicios')
        self.product = Product.objects.create(
            sku='',
            name='Consultoria',
            description='Servicio de consultoria',
            category=self.category,
            sale_price=100,
            cost_price=50,
            tax=self.tax,
        )

    def test_budget_number_is_generated(self):
        invoice = Invoice.objects.create(customer=self.customer, issue_date=date(2026, 7, 14))

        self.assertEqual(invoice.invoice_number, 'PRE-1407-01')

    def test_document_converts_from_budget_to_invoice(self):
        invoice = Invoice.objects.create(customer=self.customer, issue_date=date(2026, 7, 14))
        invoice.document_type = Invoice.DocumentType.INVOICE
        invoice.save()

        self.assertEqual(invoice.invoice_number, 'FAC-1407-01')

    def test_document_keeps_sequence_when_converted(self):
        invoice = Invoice.objects.create(customer=self.customer, issue_date=date(2026, 7, 14))

        invoice.document_type = Invoice.DocumentType.INVOICE
        invoice.save()

        self.assertEqual(invoice.document_sequence, 1)
        self.assertEqual(invoice.invoice_number, 'FAC-1407-01')

    def test_invoice_line_calculates_amounts(self):
        invoice = Invoice.objects.create(customer=self.customer, issue_date=date(2026, 7, 14))
        line = InvoiceLine.objects.create(
            invoice=invoice,
            product=self.product,
            description='',
            quantity=2,
            unit_price=self.product.sale_price,
            tax_percentage=self.tax.percentage,
        )

        invoice.recalculate_totals()

        self.assertEqual(line.line_subtotal, 200)
        self.assertEqual(line.tax_amount, 42)
        self.assertEqual(line.line_total, 242)
        invoice.refresh_from_db()
        self.assertEqual(invoice.subtotal, 200)
        self.assertEqual(invoice.tax_total, 42)
        self.assertEqual(invoice.total, 242)


class InvoiceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='admin', email='admin@example.com', password='pass1234', role=User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.customer = CustomerUser.objects.create(
            customer_type=CustomerUser.CustomerType.COMPANY,
            billing_name='Cliente API',
            tax_id='B12345678',
            address='Calle API 1',
            city='Madrid',
            province='Madrid',
            contact_email='api@example.com',
        )
        self.tax = Tax.objects.create(name='IVA', percentage=21)
        self.category = Category.objects.create(name='Servicios API')
        self.product = Product.objects.create(
            sku='',
            name='Servicio API',
            description='Servicio',
            category=self.category,
            sale_price=100,
            cost_price=50,
            tax=self.tax,
        )

    def test_create_invoice_api(self):
        payload = {
            'customer': self.customer.id,
            'notes': 'Creada por API',
            'lines': [
                {
                    'product': self.product.id,
                    'description': '',
                    'quantity': 2,
                    'unit_price': 100,
                    'tax_percentage': 21,
                }
            ]
        }

        response = self.client.post('/api/invoices/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['document_type'], Invoice.DocumentType.BUDGET)
        self.assertEqual(response.data['invoice_number'], 'PRE-1407-01')
        self.assertEqual(response.data['customer_name'], 'Cliente API')
        self.assertEqual(len(response.data['lines']), 1)

    def test_list_invoices_api(self):
        Invoice.objects.create(customer=self.customer, issue_date='2026-07-14')
        response = self.client.get('/api/invoices/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
