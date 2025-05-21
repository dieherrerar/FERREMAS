from rest_framework import serializers

class ProductoSerializer(serializers.Serializer):
    id_producto = serializers.IntegerField()
    nombre = serializers.CharField(max_length=255)
    descripcion = serializers.CharField()
    categoria = serializers.CharField(max_length=255)
    marca = serializers.CharField(max_length=255)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField()
    id_sucursal = serializers.IntegerField()
    sucursal = serializers.CharField(max_length=255)

class CategoriaSerializer(serializers.Serializer):
    categoria = serializers.CharField()

class StockSucursalSerializer(serializers.Serializer):
    producto =serializers.CharField(max_length=255)
    stock = serializers.IntegerField()
    sucursal = serializers.CharField(max_length=255)

class ContactoSerializer(serializers.Serializer):
    correo = serializers.EmailField(help_text="Correo elecronico del usuario o cliente" )
    mensaje = serializers.CharField(help_text="Mensaje a enviar")
    id_sucursal = serializers.IntegerField(help_text="Id de la sucursal a enviar (1, 2 o 3)")