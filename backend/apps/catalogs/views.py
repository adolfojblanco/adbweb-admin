from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.catalogs.models import Category, Tax, Product
from .serializers import CategorySerializer, TaxSerializer, ProductSerializer
from apps.core.permissions import IsSellerUser, IsAdminUser


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    search_fields = ["name"]
    ordering_fields = ["name"]
    permission_classes = [IsAdminUser]


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all().order_by("name")
    serializer_class = TaxSerializer
    permission_classes = [IsAdminUser]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
