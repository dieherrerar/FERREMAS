# urls.py
from django.urls import path
from . import views, API

urlpatterns = [
    path('registro/', views.add_cliente, name='registro'),
    path('add_producto/', views.add_product, name='add_producto'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('', views.home, name = 'home'),
    path('logout/', views.logout, name='logout'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('herr_manuales/', views.herr_manuales, name='herr_manuales'),
    path('materiales_basicos/', views.materiales_basicos, name='materiales_basicos'),
    path('eq_seguridad/', views.eq_seguridad, name='eq_seguridad'),
    path('eq_medicion/', views.eq_medicion, name='eq_medicion'),
    path('adhesivos/', views.adhesivos, name='adhesivos'),
    path('tor_ancl/', views.tor_ancl, name='tor_ancl'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('modificar-cantidad/<int:id_producto>/', views.modificar_cantidad, name='modificar_cantidad'),
    path('eliminar/<int:id_producto>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('agregar-carrito/<int:id_producto>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('modificar_prod/<int:id_producto>/', views.modificar_prod, name='modificar_prod'),
    path('eliminar_prod/<int:id_producto>/', views.eliminar_prod, name='eliminar_prod'),
    path('checkout/', views.checkout, name='checkout'),
    path('perfil/', views.perfil, name='perfil'),
    path('webpay/', views.pagar, name='webpay'),
    path('webpay_resultado/', views.resultado_pago, name='resultado_pago'),
    path('api_get_productos', API.api_get_productos, name="api_get_productos"),
    path('contacto_api/', API.contacto_api, name="contacto_api"),
    path('detalle_producto/<int:id>/', API.detalle_producto, name="detalle_producto"),
    path('categoria_prod/', API.categoria_prod, name="categoria_prod"),
    path('stock_sucursal/<int:id>/', API.stock_sucursal, name="stock_sucursal"),
    path('contacto_usuario/', views.contacto_usuario, name="contacto_usuario" ),
    path('marcar_leido', views.marcar_leido, name="marcar_leido")
]
