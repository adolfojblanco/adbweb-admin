from rest_framework import serializers
from .models import User, CustomerUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = "__all__"