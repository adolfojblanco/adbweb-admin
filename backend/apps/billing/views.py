from .serializers import PaymentMethodsSerializer

# Views for billing.

from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import PaymentMethod
from apps.core.permissions import IsAdminUser


class PaymentMethodsViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all().order_by("name")
    serializer_class = PaymentMethodsSerializer
    search_fields = ["name"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]