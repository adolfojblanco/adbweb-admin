"""
URL configuration for adbwebdesign project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
)

urlpatterns = [
    path('admin/', admin.site.urls),
    ## APPS ROUTES
    path("api/v1/catalog/", include(("apps.catalogs.urls", "catalog"), namespace="v1-catalog")),
    ## APPS ROUTES
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
