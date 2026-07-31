"""
URL configuration for adbwebdesign project.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
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

    # Billings
    path('api/', include(('apps.billing.urls', 'billings'))),

    # Core
    path('api/', include(('apps.core.urls', 'core'))),

    # SEO
    path('api/seo/', include(('apps.seo.urls', 'seo'))),

    # El logo se guarda en STATIC_ROOT (vía staticfiles_storage).
    # El dev server solo sirve desde STATICFILES_DIRS, así que exponemos
    # /static/logo.png explícitamente desde STATIC_ROOT.
    path('static/logo.png', serve, {
        'document_root': settings.STATIC_ROOT,
        'path': 'logo.png',
    }),

    # Docu routes
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
