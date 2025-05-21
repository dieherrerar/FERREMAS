from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from .serializers import ProductoSerializer, CategoriaSerializer, StockSucursalSerializer, ContactoSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='get',
    operation_description="Listar todos los productos disponibles en las distintas sucursales de Ferremas",
    responses={
        200: ProductoSerializer(many=True),
    }
)

@api_view(['GET'])
def api_get_productos(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT p.id_producto AS id_producto, 
                        p.nombre AS nombre, 
                        p.descripcion AS descripcion, 
                        p.categoria AS categoria, 
                        p.marca AS marca, 
                        p.precio AS precio, 
                        p.cantidad AS stock, 
                        p.id_sucursal AS id_sucursal, 
                        CONCAT(s.nombre, ' ', s.direccion) AS sucursal
                        FROM producto p JOIN sucursal s
                        WHERE p.id_sucursal = s.id_sucursal """)
        columnas = [col[0] for col in cursor.description] #crea una lista con los nombres de las columnas que vienen en la respuesta de la consulta.
        productos=[
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]
        
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)



@swagger_auto_schema(
    method='get',
    operation_description="Seleccionar detalles de un producto a traves de su id",
    responses={
        200: ProductoSerializer(many=True),
        400: openapi.Response('El producto no existe')
    }
)

@api_view(['GET'])
def detalle_producto(request, id):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT p.id_producto AS id_producto, 
                        p.nombre AS nombre, 
                        p.descripcion AS descripcion, 
                        p.categoria AS categoria, 
                        p.marca AS marca, 
                        p.precio AS precio, 
                        p.cantidad AS stock, 
                        p.id_sucursal AS id_sucursal, 
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


@swagger_auto_schema(
    method='get',
    operation_description="Seleccionar las categorias de los productos existentes",
    responses={
        200: CategoriaSerializer(many=True),
    }
)


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



@swagger_auto_schema(
    method='get',
    operation_description="Obtiene el stock por sucursal",
    responses={
        200: StockSucursalSerializer(many=True),
        404: openapi.Response('Sucursal no existe o datos inválidos')
    }
)
@api_view(['GET'])
def stock_sucursal(request, id):
        
    if id not in [1, 2, 3]:
        return Response(
            {'error': 'Sucursal ingresada no existe'}, status=404)

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




@swagger_auto_schema(
    method='post',
    operation_description="Envía un mensaje de contacto",
    request_body=ContactoSerializer,
    responses={
        201: openapi.Response('Mensaje enviado correctamente'),
        404: openapi.Response('Sucursal no existe o datos inválidos')
    }
)

@csrf_exempt
@api_view(['POST'])
def contacto_api(request):
    id_sucursal = request.data.get('id_sucursal')

    if id_sucursal not in [1,2,3]:
        return Response({'error': 'Sucursal ingresada no existe'}, status=404)


    serializer = ContactoSerializer(data=request.data)
    if serializer.is_valid():
        correo = serializer.validated_data['correo']
        mensaje = serializer.validated_data['mensaje']
        id_sucursal = serializer.validated_data['id_sucursal']

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO mensajes_contacto (correo, mensaje, id_sucursal)
                              VALUES (%s,%s,%s)""", [correo, mensaje, id_sucursal])
        
        return Response({'detail': 'Mensaje enviado correctamente'}, status=201)
    
    return Response(serializer.errors, status=400)