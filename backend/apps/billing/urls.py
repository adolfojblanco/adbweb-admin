from django.urls import path
from .views import export_invoice_pdf

# Importante: No pongas barras '/' al principio de los strings de path
urlpatterns = [
    path('invoice/<int:invoice_id>/pdf/', export_invoice_pdf, name='invoice_pdf_final'),
]