from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('FerremasHome.urls')),  # Ajusta el nombre 'clientes' según cómo se llame tu app
]
