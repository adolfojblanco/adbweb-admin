from django.db.models import TextChoices


class Currency(TextChoices):
    EUR = "EUR", "Euro"
    USD = "USD", "US Dollar"


class InvoiceStatus(TextChoices):
    DRAFT = "DRAFT", "Borrador"
    ISSUED = "ISSUED", "Emitida"
    PAID = "PAID", "Pagada"
    CANCELLED = "CANCELLED", "Anulada"


class PaymentStatus(TextChoices):
    PENDING = "PENDING", "Pendiente"
    CONFIRMED = "CONFIRMED", "Confirmado"
