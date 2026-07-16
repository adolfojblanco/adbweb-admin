from rest_framework import serializers

from apps.core.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'email_company',
            'phone',
            'website',
            'address',
            'city',
            'state',
            'postal_code',
            'logo',
        ]
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        new_logo = validated_data.get('logo')
        if new_logo and instance.logo:
            instance.logo.delete(save=False)
        return super().update(instance, validated_data)
