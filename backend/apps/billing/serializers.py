from rest_framework import serializers
from .models import PaymentMethod


class PaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "name", "is_active"]