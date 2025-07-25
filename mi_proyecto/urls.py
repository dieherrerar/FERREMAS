from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
        openapi.Info(
            title="FERREMAS_API",
            default_version='v1',
            description="API de la ferreteria FERREMAS, en la cual podrás consultar productos, detalles, contactar, etc.",
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('FerremasHome.urls')),  # Ajusta el nombre 'clientes' según cómo se llame tu app
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


]
