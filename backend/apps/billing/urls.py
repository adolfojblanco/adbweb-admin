from rest_framework.routers import DefaultRouter
from .views import PaymentMethodsViewSet

# Billing Routes

router = DefaultRouter()

router.register(r"payment-methods", PaymentMethodsViewSet, basename="payment-methods")

urlpatterns = router.urls