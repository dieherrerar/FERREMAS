from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from .serializers import ProductoSerializer, CategoriaSerializer, StockSucursalSerializer



@api_view(['GET'])
def api_get_productos(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT p.id_producto, 
                        p.nombre, p.descripcion, p.categoria, p.marca, p.precio, p.cantidad, 
                        p.id_sucursal, 
                        CONCAT(s.nombre, ' ', s.direccion) AS sucursal
                        FROM producto p JOIN sucursal s
                        WHERE p.id_sucursal = s.id_sucursal""")
        columnas = [col[0] for col in cursor.description] #crea una lista con los nombres de las columnas que vienen en la respuesta de la consulta.
        productos=[
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]
        
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def detalle_producto(request, id):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT p.id_producto, 
                        p.nombre, p.descripcion, p.categoria, p.marca, p.precio, p.cantidad, 
                        p.id_sucursal, 
                        CONCAT(s.nombre, ' ', s.direccion) AS sucursal
                        FROM producto p JOIN sucursal s
                        WHERE p.id_sucursal = s.id_sucursal 
                        AND p.id_producto = %s""", [id])
        producto = cursor.fetchone()

        if producto:
            columnas = [col[0] for col in cursor.description]
            producto_det = dict(zip(columnas, producto))
            serializer = ProductoSerializer(producto_det)
            return Response(serializer.data)
        return Response({'error': 'Producto no existe'}, status=404)



@api_view(['GET'])
def categoria_prod(request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT categoria FROM producto")
            columnas = [col[0] for col in cursor.description]
            categorias=[
                {'categoria': fila[0]}
                for fila in cursor.fetchall()
            ]
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def stock_sucursal(request, id):
        with connection.cursor() as cursor:
            cursor.execute("""SELECT p.nombre AS producto, 
                              p.cantidad AS stock, 
                              CONCAT(s.nombre, ' ', s.direccion) AS sucursal  
                              FROM producto p JOIN sucursal s ON p.id_sucursal = s.id_sucursal
                              WHERE p.id_sucursal = %s""", [id])

            columnas = [col[0] for col in cursor.description] #crea una lista con los nombres de las columnas que vienen en la respuesta de la consulta.
            stocks=[
                dict(zip(columnas, fila))
                for fila in cursor.fetchall()
            ]
        
        serializer = StockSucursalSerializer(stocks, many=True)
        return Response(serializer.data)
