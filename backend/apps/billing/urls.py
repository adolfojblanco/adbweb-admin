from rest_framework.routers import DefaultRouter

from apps.billing.views import SupplierViewSet, InvoiceViewSet, PaymentMethodViewSet

router = DefaultRouter()

router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"payment-methods", PaymentMethodViewSet, basename="payment-method")

urlpatterns = router.urls
