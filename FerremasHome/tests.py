from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Producto

class ProductoTestCase(TestCase):
    
    def setUp(self):
        """Este método se ejecuta antes de cada prueba. Crea los datos que se usarán."""
        self.producto = Producto.objects.create(
            nombre="Martillo",
            descripcion="Martillo de acero",
            categoria="Herramientas",
            marca="Marca A",
            precio=1000.0,
            cantidad=50,
            is_active=True
        )

    def test_producto_creado(self):
        """Prueba si el producto se crea correctamente en la base de datos"""
        producto = Producto.objects.get(nombre="Martillo")
        self.assertEqual(producto.precio, 1000.0)  # Verifica que el precio sea el esperado
        self.assertTrue(producto.is_active)  # Verifica que 'is_active' sea True

    def test_producto_no_existente(self):
        """Prueba que el producto no existe si no se crea"""
        with self.assertRaises(Producto.DoesNotExist):
            Producto.objects.get(nombre="Producto Inexistente")

    def test_producto_campos_vacios(self):
        """Prueba que no se pueda crear un producto con campos obligatorios vacíos"""
        producto = Producto(
            nombre='',  # Nombre vacío, debería causar un error
            descripcion="Martillo sin marca",
            categoria="Herramientas",
            marca="Marca B",
            precio=1500.0,
            cantidad=20,
            is_active=True
        )
        with self.assertRaises(ValidationError):
            producto.full_clean()  # Llamamos a full_clean para que se dispare la validación

    def test_producto_precio_negativo(self):
        """Prueba que no se pueda crear un producto con un precio negativo"""
        producto = Producto(
            nombre="Sierra",
            descripcion="Sierra de mano",
            categoria="Herramientas",
            marca="Marca D",
            precio=-50.0,  # Precio negativo, debería causar un error
            cantidad=10,
            is_active=True
        )
        with self.assertRaises(ValidationError):
            producto.full_clean()  # Llamamos a full_clean para que se dispare la validación

    def test_producto_actualizacion(self):
        """Prueba actualizacion de precio"""
        producto = Producto.objects.get(nombre="Martillo")
        producto.precio = 1200.0  # Actualizamos el precio
        producto.save()  # Guardamos el cambio

        # Verificamos que el precio se haya actualizado
        producto_actualizado = Producto.objects.get(nombre="Martillo")
        self.assertEqual(producto_actualizado.precio, 1200.0)
