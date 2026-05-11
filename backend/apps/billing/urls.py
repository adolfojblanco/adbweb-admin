from rest_framework.routers import DefaultRouter
from .views import PaymentMethodsViewSet, SupplierViewSet

# Billing Routes

router = DefaultRouter()

router.register(r"payment-methods", PaymentMethodsViewSet, basename="payment-methods"),
router.register(r"suppliers", SupplierViewSet, basename="suppliers")

urlpatterns = router.urls