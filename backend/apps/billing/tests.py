from datetime import date

from django.test import TestCase

from apps.accounts.models import Customer, User
from apps.billing.models import Invoice, InvoiceItem
from apps.billing.serializers import InvoiceSerializer
from apps.catalogs.models import Category, Product
from apps.core.models import Tax
from rest_framework.test import APIClient


class InvoiceModelTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='seller', email='seller@example.com',
            password='pass1234', role=User.Role.SELLER,
        )
        self.customer = Customer.objects.create(
            customer_type=Customer.CustomerType.COMPANY,
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
        invoice = Invoice.objects.create(
            customer=self.customer,
            seller=self.seller,
            tax=self.tax,
            issue_date=date(2026, 7, 14),
        )

        self.assertTrue(invoice.number.startswith('PRE-2026-'))
        self.assertEqual(invoice.document_type, Invoice.DocumentType.QUOTE)

    def test_document_converts_from_budget_to_invoice(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            seller=self.seller,
            tax=self.tax,
            issue_date=date(2026, 7, 14),
        )
        invoice.document_type = Invoice.DocumentType.INVOICE
        invoice.save()

        self.assertTrue(invoice.number.startswith('FAC-2026-'))
        self.assertEqual(invoice.document_type, Invoice.DocumentType.INVOICE)

    def test_invoice_item_calculates_subtotal(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            seller=self.seller,
            tax=self.tax,
            issue_date=date(2026, 7, 14),
        )
        item = InvoiceItem.objects.create(
            invoice=invoice,
            product=self.product,
            product_name=self.product.name,
            quantity=2,
            unit_price=self.product.sale_price,
        )

        self.assertEqual(item.subtotal, 200)

        invoice.update_totals()
        invoice.refresh_from_db()

        self.assertEqual(invoice.subtotal, 200)
        self.assertEqual(invoice.tax_amount, 42)
        self.assertEqual(invoice.total, 242)


class InvoiceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='admin', email='admin@example.com', password='pass1234', role=User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.seller = self.user
        self.customer = Customer.objects.create(
            customer_type=Customer.CustomerType.COMPANY,
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
            'tax': self.tax.id,
            'notes': 'Creada por API',
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 2,
                    'unit_price': 100,
                }
            ]
        }

        response = self.client.post('/api/invoices/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['document_type'], Invoice.DocumentType.QUOTE)
        self.assertTrue(response.data['number'].startswith('PRE-'))
        self.assertEqual(response.data['customer_name'], 'Cliente API')
        self.assertEqual(response.data['seller'], self.user.id)
        self.assertEqual(len(response.data['items']), 1)

    def test_list_invoices_api(self):
        Invoice.objects.create(
            customer=self.customer,
            seller=self.seller,
            tax=self.tax,
            issue_date='2026-07-14',
        )
        response = self.client.get('/api/invoices/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_issue_action_converts_quote_to_invoice(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            seller=self.seller,
            tax=self.tax,
            issue_date=date(2026, 7, 14),
        )
        self.assertEqual(invoice.document_type, Invoice.DocumentType.QUOTE)
        self.assertTrue(invoice.number.startswith('PRE-'))

        response = self.client.post(f'/api/invoices/{invoice.id}/issue/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['document_type'], Invoice.DocumentType.INVOICE)
        self.assertEqual(response.data['status'], Invoice.Status.ISSUED)
        self.assertTrue(response.data['number'].startswith('FAC-'))
