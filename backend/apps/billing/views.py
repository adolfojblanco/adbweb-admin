from .serializers import PaymentMethodsSerializer, SupplierSerializer, InvoiceSerializer, InvoiceItemSerializer
from apps.core.views import CoreModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import PaymentMethod, Supplier, Invoice, InvoiceItem
from apps.core.permissions import IsAdminUser

# Views for billing.

class PaymentMethodsViewSet(CoreModelViewSet):
    queryset = PaymentMethod.objects.all().order_by("name")
    serializer_class = PaymentMethodsSerializer
    search_fields = ["name"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]


class SupplierViewSet(CoreModelViewSet):
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer
    search_fields = ["name"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

class InvoiceViewSet(CoreModelViewSet):
    """
    API endpoint que permite ver, crear, editar o borrar Facturas.
    """
    queryset = Invoice.objects.all().order_by('-issue_date', '-id')
    serializer_class = InvoiceSerializer

class InvoiceItemViewSet(CoreModelViewSet):
    """
    API endpoint para gestionar las líneas de detalle de forma individual.
    """
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer


