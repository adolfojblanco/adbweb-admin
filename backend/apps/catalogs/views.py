from rest_framework import viewsets

from apps.catalogs.models import Category, Tax
from .serializers import CategorySerializer, TaxSerializer
from ..accounts.permissions import ReadOnlyOrAdminSeller


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminSeller]
    search_fields = ["name"]
    ordering_fields = ["name"]


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all().order_by("name")
    serializer_class = TaxSerializer
    permission_classes = [ReadOnlyOrAdminSeller]
