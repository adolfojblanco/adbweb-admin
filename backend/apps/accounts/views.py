from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics, filters, status
from .models import CustomerUser

from .serializers import UserSerializer, CustomerSerializer
from apps.core.views import TimeStampedViewSet


# View for accounts

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CustomerViewSet(TimeStampedViewSet):
    queryset = CustomerUser.objects.all().order_by('billing_name')
    serializer_class = CustomerSerializer
    lookup_value_regex = r'\d+'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        from apps.billing.models import Invoice
        issued_count = Invoice.objects.filter(
            customer=instance,
            status__in=[Invoice.Status.ISSUED, Invoice.Status.PAID, Invoice.Status.CANCELLED],
        ).count()
        if issued_count > 0:
            return Response(
                {'detail': f'No se puede eliminar el cliente porque tiene {issued_count} factura(s) emitida(s), pagada(s) o cancelada(s).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class CustomerSearchView(generics.ListAPIView):
    queryset = CustomerUser.objects.all().order_by('billing_name')
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['billing_name', 'tax_id', 'contact_email']
