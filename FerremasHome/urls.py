# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.add_cliente, name='registro'),
    path('add_producto/', views.add_product, name='add_producto'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('', views.home, name = 'home'),
    path('logout/', views.logout, name='logout'),
    path('admin_login/', views.admin_login, name='admin_login'),
]
