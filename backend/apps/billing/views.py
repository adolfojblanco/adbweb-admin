from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Invoice


def export_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    template_path = 'billing/invoice_pdf.html'
    context = {'invoice': invoice}

    # Crear la respuesta de Django como tipo PDF
    response = HttpResponse(content_type='application/pdf')
    # attachment = descarga directa | inline = abre en el navegador
    response['Content-Disposition'] = f'inline; filename="{invoice.number}.pdf"'

    # Cargar la plantilla y renderizarla con los datos
    template = get_template(template_path)
    html = template.render(context)

    # Convertir el HTML en PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response