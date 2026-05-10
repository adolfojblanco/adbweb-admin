from rest_framework import serializers

from .models import Tax, Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active']


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = '__all__'


# apps/catalogs/serializers.py
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        # 1. Obtenemos la data original (que tiene los IDs)
        response = super().to_representation(instance)

        # 2. Inyectamos los objetos completos en la respuesta
        if instance.category:
            response['category'] = CategorySerializer(instance.category).data
        if instance.tax:
            response['tax'] = TaxSerializer(instance.tax).data

        return response