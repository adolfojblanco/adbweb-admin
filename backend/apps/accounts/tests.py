from django.test import TestCase
from rest_framework.test import APIClient

from .models import CustomerUser, User


class CustomerUserModelTests(TestCase):
    def test_save_normalizes_contact_data(self):
        customer = CustomerUser.objects.create(
            customer_type=CustomerUser.CustomerType.COMPANY,
            billing_name='acme sl',
            tax_id='abc123',
            address='Calle Mayor 1',
            city='Madrid',
            province='Madrid',
            contact_email='INFO@ACME.COM',
            phone='600000000',
        )

        self.assertEqual(customer.contact_email, 'info@acme.com')
        self.assertEqual(customer.billing_name, 'Acme Sl')
        self.assertEqual(customer.tax_id, 'Abc123')

    def test_signal_creates_user_for_new_customer(self):
        customer = CustomerUser.objects.create(
            customer_type=CustomerUser.CustomerType.PERSON,
            billing_name='Cliente Uno',
            tax_id='12345678a',
            address='Calle Uno 1',
            city='Valencia',
            province='Valencia',
            contact_email='cliente1@example.com',
        )

        customer.refresh_from_db()

        self.assertIsNotNone(customer.user)
        self.assertEqual(customer.user.role, User.Role.CLIENT)
        self.assertEqual(customer.user.email, 'cliente1@example.com')
        self.assertEqual(customer.user.username, 'clienteuno')


class CustomerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_customer_endpoint_creates_customer_and_user(self):
        payload = {
            'customer_type': 'COMPANY',
            'billing_name': 'Example Sa',
            'tax_id': 'B12345678',
            'address': 'Calle Falsa 123',
            'city': 'Madrid',
            'province': 'Madrid',
            'postal_code': '28001',
            'contact_email': 'contact@example.com',
            'phone': '900123123',
        }

        response = self.client.post('/api/auth/customers/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomerUser.objects.count(), 1)
        customer = CustomerUser.objects.first()
        self.assertIsNotNone(customer.user)
        self.assertEqual(response.data['billing_name'], 'Example Sa')

    def test_list_and_search_customers_endpoint(self):
        CustomerUser.objects.create(
            customer_type=CustomerUser.CustomerType.PERSON,
            billing_name='Cliente A',
            tax_id='11111111A',
            address='Calle A 1',
            city='Sevilla',
            province='Sevilla',
            contact_email='a@example.com',
        )
        CustomerUser.objects.create(
            customer_type=CustomerUser.CustomerType.COMPANY,
            billing_name='Cliente B',
            tax_id='22222222B',
            address='Calle B 2',
            city='Barcelona',
            province='Barcelona',
            contact_email='b@example.com',
        )

        list_response = self.client.get('/api/auth/customers/')
        search_response = self.client.get('/api/auth/customers/search/?search=Cliente B')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 2)
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(len(search_response.data), 1)
        self.assertEqual(search_response.data[0]['billing_name'], 'Cliente B')
