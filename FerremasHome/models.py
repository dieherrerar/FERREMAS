from django.core.exceptions import ValidationError
from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)  # Nombre obligatorio
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)  # Precio obligatorio
    cantidad = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        """Verifica que el precio no sea negativo"""
        if self.precio < 0:
            raise ValidationError('El precio no puede ser negativo')

    def __str__(self):
        return self.nombre
