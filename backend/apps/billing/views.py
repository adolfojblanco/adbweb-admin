from django.shortcuts import render
from rest_framework import viewsets

from apps.billing.models import Supplier
from apps.billing.serializers import SupplierSerializer


# Create your views here.


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer
