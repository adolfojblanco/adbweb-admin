from django.urls import path

from apps.core.views import CompanyView

urlpatterns = [
    path('company/', CompanyView.as_view(), name='company-detail'),
]
