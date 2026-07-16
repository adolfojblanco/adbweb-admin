from rest_framework import serializers
from .models import User, Customer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
<<<<<<< HEAD
        model = Customer
        fields = "__all__"
=======
        model = CustomerUser
        fields = [
            'id',
            'customer_type',
            'billing_name',
            'tax_id',
            'address',
            'city',
            'province',
            'postal_code',
            'contact_email',
            'phone',
            'user',
        ]
>>>>>>> develop
