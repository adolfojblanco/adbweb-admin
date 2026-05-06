"""
URL configuration for adbwebdesign project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="ADB Web & Design API",
        default_version='v1',
        description="API for adbwebdesign admin site",
        terms_of_service="https://adbwebdesign.com/",
        contact=openapi.Contact(email="me@adolfob.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Admin Routes
    path('api/auth/', include('apps.accounts.urls')),

    # Inventories
    path('api/', include(('apps.catalogs.urls', 'catalogs'))),
    path('api/', include(('apps.billing.urls', 'billing'))),


    # Docu routes
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
