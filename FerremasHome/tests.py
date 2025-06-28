# tests.py

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
