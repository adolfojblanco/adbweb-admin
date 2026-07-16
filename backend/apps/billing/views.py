import os
from email.mime.image import MIMEImage
from email.utils import formataddr
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.billing.models import Supplier, Invoice, PaymentMethod
from apps.billing.serializers import SupplierSerializer, InvoiceSerializer, PaymentMethodSerializer
from apps.core.models import Company
from apps.core.views import TimeStampedViewSet


# Billing Views.


def _resolve_logo_path(company):
    if company.logo and company.logo.name:
        candidate = company.logo.path
        if os.path.exists(candidate):
            return candidate
    fallback = os.path.join(settings.STATIC_ROOT, 'logo.png')
    return fallback if os.path.exists(fallback) else None


def _document_label(invoice):
    return 'Factura' if invoice.document_type == invoice.DocumentType.INVOICE else 'Presupuesto'


def _document_slug(invoice):
    return 'factura' if invoice.document_type == invoice.DocumentType.INVOICE else 'presupuesto'


def generate_invoice_pdf(invoice, company):
    html = render_to_string('billing/pdf/invoice.html', {
        'invoice': invoice,
        'company': company,
        'document_label': _document_label(invoice),
        'logo_path': _resolve_logo_path(company),
    })
    pdf_buffer = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer)
    return pdf_buffer.getvalue()


class SupplierViewSet(TimeStampedViewSet):
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer


class PaymentMethodViewSet(TimeStampedViewSet):
    queryset = PaymentMethod.objects.all().order_by('name')
    serializer_class = PaymentMethodSerializer


class InvoiceViewSet(TimeStampedViewSet):
    queryset = Invoice.objects.select_related('customer').prefetch_related('lines', 'lines__product').all().order_by('-issue_date', '-id')
    serializer_class = InvoiceSerializer

    @action(detail=True, methods=['post'])
    def convert_to_invoice(self, request, pk=None):
        invoice = self.get_object()
        if invoice.document_type != invoice.DocumentType.INVOICE:
            invoice.document_type = invoice.DocumentType.INVOICE
            invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='set-status')
    def set_status(self, request, pk=None):
        invoice = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in Invoice.Status.choices]
        if new_status not in valid_statuses:
            return Response(
                {'status': f'Estado inválido. Opciones: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.status = new_status
        invoice.save(update_fields=['status', 'updated_at', 'updated_by'])
        serializer = self.get_serializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='send-email')
    def send_email(self, request, pk=None):
        invoice = self.get_object()
        company = Company.objects.first()

        if not company:
            return Response(
                {'detail': 'No hay empresa configurada. Crea una empresa antes de enviar facturas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not invoice.customer.contact_email:
            return Response(
                {'detail': 'El cliente no tiene un email de contacto.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        document_label = _document_label(invoice)

        html_content = render_to_string('billing/email/invoice.html', {
            'invoice': invoice,
            'company': company,
            'document_label': document_label,
        })

        subject = f'{document_label} {invoice.invoice_number} - {company.name}'

        from_email = formataddr((company.name, company.email_company)) if company.email_company else settings.DEFAULT_FROM_EMAIL

        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=from_email,
            to=[invoice.customer.contact_email],
        )
        email.content_subtype = 'html'

        logo_path = _resolve_logo_path(company)
        if logo_path:
            ext = os.path.splitext(logo_path)[1].lower().lstrip('.')
            subtype = ext if ext in ('png', 'jpg', 'jpeg', 'gif') else 'png'
            with open(logo_path, 'rb') as f:
                image = MIMEImage(f.read(), _subtype=subtype)
                image.add_header('Content-ID', '<company-logo>')
                image.add_header('Content-Disposition', 'inline', filename=f'logo.{subtype}')
                email.attach(image)

        try:
            pdf_content = generate_invoice_pdf(invoice, company)
            filename = f'{_document_slug(invoice)}_{invoice.invoice_number}.pdf'
            email.attach(filename, pdf_content, 'application/pdf')
        except Exception as exc:
            return Response(
                {'detail': f'Error al generar el PDF adjunto: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        email.send()

        return Response(
            {'detail': f'Email enviado correctamente a {invoice.customer.contact_email}.'},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['get'], url_path='pdf')
    def pdf(self, request, pk=None):
        invoice = self.get_object()
        company = Company.objects.first()

        if not company:
            return Response(
                {'detail': 'No hay empresa configurada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pdf_content = generate_invoice_pdf(invoice, company)
        except Exception as exc:
            return Response(
                {'detail': f'Error al generar el PDF: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        filename = f'{_document_slug(invoice)}_{invoice.invoice_number}.pdf'
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
