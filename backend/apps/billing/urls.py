from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import export_invoice_pdf, PaymentMethodsViewSet

# Billing Routes

router = DefaultRouter()

router.register(r"payment-methods", PaymentMethodsViewSet, basename="payment-methods")

urlpatterns = [
    path('invoice/<int:invoice_id>/pdf/', export_invoice_pdf, name='invoice_pdf_final'),
] + router.urls