from rest_framework import serializers

from .models import Tax, Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    tax = TaxSerializer(read_only=True)

    class Meta:
        model = Product
