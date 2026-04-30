from rest_framework import serializers

from .models import Tax, Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'active']


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = '__all__'


# apps/catalogs/serializers.py

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def to_internal_value(self, data):
        # Mapeamos los IDs que vienen de Angular al nombre que espera Django
        if 'category_id' in data:
            data['category'] = data.pop('category_id')
        if 'tax_id' in data:
            data['tax'] = data.pop('tax_id')
        return super().to_internal_value(data)