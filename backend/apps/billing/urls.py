from rest_framework.routers import DefaultRouter
from .views import PaymentMethodsViewSet, SupplierViewSet, InvoiceViewSet, InvoiceItemViewSet

# Billing Routes

router = DefaultRouter()

router.register(r"payment-methods", PaymentMethodsViewSet, basename="payment-methods"),
router.register(r"suppliers", SupplierViewSet, basename="suppliers")
router.register(r"invoice", InvoiceViewSet, basename="invoice")
router.register(r'invoice-items', InvoiceItemViewSet, basename='invoice-item')

urlpatterns = router.urls