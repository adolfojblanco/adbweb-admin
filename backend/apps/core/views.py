from django.shortcuts import render
from rest_framework import viewsets


# Core views here.

class CoreModelViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)