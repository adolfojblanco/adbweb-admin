from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import NotFound

from apps.core.models import Company
from apps.core.serializers import CompanySerializer


class TimeStampedViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class CompanyView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_object(self):
        company = Company.objects.first()
        if not company:
            raise NotFound('No hay empresa configurada.')
        return company

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
