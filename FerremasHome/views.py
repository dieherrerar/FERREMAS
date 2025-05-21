from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
import bcrypt
from django.http import HttpResponse
import transbank.webpay.webpay_plus
from transbank.webpay.webpay_plus.transaction import Transaction
import time
from django.views.decorators.csrf import csrf_exempt
from .webpay_config import get_webpay_transaction
from django.urls import reverse
from .api_bcch import obtener_tipos_cambio








def add_cliente(request):
    if request.method == 'POST':
        pnombre = request.POST.get('pnombre')
        snombre = request.POST.get('snombre')
        apaterno = request.POST.get('apaterno')
        amaterno = request.POST.get('amaterno')
        rut = request.POST.get('rut')
        dv = request.POST.get('dv')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        contrasena2 = request.POST.get('contrasena2')

        datos_formulario = {
            'pnombre': pnombre,
            'snombre': snombre,
            'apaterno': apaterno,
            'amaterno': amaterno,
            'rut': rut,
            'dv': dv,
            'correo': correo,
        }


        if pnombre=="" or snombre=="" or apaterno=="" or amaterno=="" or rut=="" or correo=="" or contrasena=="" or contrasena2=="" or dv=="":
            return render(request, 'registro.html', {'mensaje': 'Ningún campo debe estar vacío', 'datos': datos_formulario})
        else:
            if contrasena == contrasena2:
                if contrasena and contrasena2 and (len(contrasena) < 8 or len(contrasena) > 25 or len(contrasena2) < 8 or len(contrasena2) > 25):
                    return render(request, 'registro.html', {'mensaje': 'Las contraseñas deben tener minimo 8 caracteres y máximo 25', 'datos': datos_formulario})
                else: 
                    if dv in '1234567890Kk': 
                        with connection.cursor() as cursor:
                            cursor.execute('SELECT COUNT(*) FROM usuario WHERE rut = %s', [rut])
                            rut_existe = cursor.fetchone()[0]

                            cursor.execute('SELECT COUNT(*) FROM usuario WHERE correo = %s', [correo] )
                            correo_existe = cursor.fetchone()[0]
                        if rut_existe == 0 and correo_existe == 0:
                            hashed_pw = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            rut_int = int(rut)
                            try: 
                                with connection.cursor() as cursor:
                                    sql = """
                                        INSERT INTO usuario (pnombre, snombre, apaterno, amaterno, rut, correo, contrasena, dv)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    """
                                    cursor.execute(sql, [pnombre, snombre, apaterno, amaterno, rut_int, correo, hashed_pw, dv])
                    
                                return redirect('home')
                            except IntegrityError as e:
                                return render(request, 'registro.html', {'mensaje': 'Error al registrar el cliente, por favor intente de nuevo', 'datos': datos_formulario})
                        else:
                            return render(request, 'registro.html', {'mensaje':'El RUT o el correo ya se encuentran registrados', 'datos': datos_formulario})
                    else:
                        return render(request, 'registro.html', {'dv':'El dígito verificador debe ser del 0 al 9 o letra k', 'datos': datos_formulario})

            else:
                return render(request, 'registro.html', {'mensaje': 'Las contraseñas no coinciden', 'datos': datos_formulario})
                
    return render(request, 'registro.html')



def add_product(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        marca = request.POST.get('marca')
        precio = request.POST.get('precio')
        cantidad = request.POST.get('cantidad')

        sucursal = request.session.get('admin_sucursal')
        id_sucursal = None  # <- Añade esta línea para inicializarla

        if sucursal == 'Viña del Mar':
            id_sucursal = 1
        elif sucursal == 'Valparaíso':
            id_sucursal = 2
        elif sucursal == 'Santiago':
            id_sucursal = 3

        # Validación de existencia de id_sucursal
        if id_sucursal is None:
            return HttpResponse("Error: No se ha podido identificar la sucursal del administrador.", status=400)

        datos_formulario = {
            'nombre': nombre,
            'descripcion': descripcion,
            'marca': marca,
            'precio': precio,
            'cantidad': cantidad,
        }

        if not all([nombre, descripcion, categoria, marca, precio, cantidad]):
            return render(request, 'add_producto.html', {'mensaje': 'Ningún campo debe estar vacío', 'datos': datos_formulario})

        with connection.cursor() as cursor:
            sql = """
                INSERT INTO producto (nombre, descripcion, categoria, marca, precio, cantidad, id_sucursal)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [nombre, descripcion, categoria, marca, precio, cantidad, id_sucursal])

        return redirect('home')

    return render(request, 'add_producto.html')



def modificar_prod(request, id_producto):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        marca = request.POST.get('marca')
        precio = request.POST.get('precio')
        cantidad = request.POST.get('cantidad')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE producto
                SET nombre = %s, descripcion = %s, precio = %s, marca = %s, categoria = %s, cantidad = %s
                WHERE id_producto = %s
            """, [nombre, descripcion, precio, marca, categoria, cantidad, id_producto ])
        
        return redirect('home')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre, descripcion, categoria, marca, precio, cantidad FROM producto WHERE id_producto = %s", [id_producto])
        producto = cursor.fetchone()

    if producto:
        producto_dic ={
            'id_producto': id_producto,
            'nombre': producto[0],
            'descripcion': producto[1],
            'categoria': producto[2],
            'marca': producto[3],
            'precio': producto[4],
            'cantidad': producto[5]
        }
        return render(request, 'modificar.html', {'producto': producto_dic})
    else:
        return HttpResponse('Producto no encontrado', status=404)



def eliminar_prod (request, id_producto):
    if request.method=='POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM producto WHERE id_producto = %s", [id_producto])
        return redirect('home')
    else:
        return render(request, 'modificar.html')



def iniciar_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        with connection.cursor() as cursor:
            cursor.execute (" SELECT * FROM usuario WHERE correo = %s", [correo])
            usuario = cursor.fetchone()
        if usuario:
            usuario_id=usuario[0]
            usuario_name=usuario[1]
            contrasena_hash=usuario[7].encode('utf-8')
            if bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash):
                request.session['usuario_id'] = usuario_id
                request.session['nombre_usuario'] = usuario_name
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Datos ingresados son incorrectos'})
        else:
            return render(request, 'login.html', {'error': 'Datos ingresados son incorrectos'})
    return render(request, 'login.html')



def home(request):
    nombre = None
    sucursal = None 
    id_sucursal = None

    if request.method == "POST":
        id_sucursal = request.POST.get('id_sucursal')
        request.session['id_sucursal'] = id_sucursal
        return redirect('home')

    if request.session.get('usuario_id'):
        nombre = request.session.get('nombre_usuario')
    elif request.session.get('admin_id'):
        nombre = request.session.get('admin_name')
        sucursal = request.session.get('admin_sucursal')

        if sucursal == 'Viña del Mar':
            id_sucursal = 1
        elif sucursal == 'Valparaíso':
            id_sucursal = 2
        elif sucursal == 'Santiago':
            id_sucursal = 3
    
    if not id_sucursal:
        id_sucursal = request.session.get('id_sucursal')


    with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nombre, id_producto, descripcion, categoria, marca, precio, cantidad 
                FROM producto 
                WHERE id_sucursal = %s
            """, [id_sucursal])
            productos = cursor.fetchall()

    tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

    productos_dic = []
    for p in productos:
        precio_clp =p[5]
        producto = {
            'nombre':p[0],
            'id_producto': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': precio_clp,
            'precio_usd': round(precio_clp / tipo_usd, 2),
            'precio_eur': round(precio_clp / tipo_eur, 2),
            'precio_ars': round(precio_clp / tipo_ars, 2),
            'cantidad': p[6]

        }
        productos_dic.append(producto)

    return render(request, 'home.html', {'productos': productos_dic, 'nombre': nombre, 'sucursal': sucursal})



def logout(request):
    request.session.flush()
    return redirect('home')



def admin_login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        rut = request.POST.get('rut')

        with connection.cursor() as cursor:
            cursor.execute (" SELECT * FROM administrador WHERE correo = %s AND rut =%s", [correo, rut])
            admin = cursor.fetchone()
        if admin:
            admin_id=admin[0]
            admin_name = admin[1]
            admin_sucursal = admin[8]
            contrasena_hash = admin[7].encode('utf-8')
            if bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash):
                request.session['admin_id'] = admin_id
                request.session['admin_name'] = admin_name
                request.session['id_sucursal'] = admin_sucursal

                if admin_sucursal == 1:
                    request.session['admin_sucursal'] = 'Viña del Mar'
                elif admin_sucursal == 2:
                    request.session['admin_sucursal'] = 'Valparaíso'
                elif admin_sucursal == 3:
                    request.session['admin_sucursal'] = 'Santiago'

                return redirect('home')
            else:
                return render(request, 'admin_login.html', {'error': 'Datos ingresados son incorrectos'})
        else:
            return render(request, 'admin_login.html', {'error': 'Datos ingresados son incorrectos'})
    
    return render(request, 'admin_login.html')



def herr_manuales(request):
    categoria = 'Herramientas Manuales'
    id_sucursal = request.session.get('id_sucursal')

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s AND id_sucursal = %s', [categoria, id_sucursal])
        productos = cursor.fetchall()

    tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

    productos_dic = []
    for p in productos:
        precio_clp =p[5]
        producto = {
            'id_producto': p[0],
            'nombre':p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': precio_clp,
            'precio_usd': round(precio_clp / tipo_usd, 2),
            'precio_eur': round(precio_clp / tipo_eur, 2),
            'precio_ars': round(precio_clp / tipo_ars, 2),
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})



def eq_seguridad(request):
    categoria = 'Equipos de Seguridad'
    id_sucursal = request.session.get('id_sucursal')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s AND id_sucursal = %s', [categoria, id_sucursal])
        productos = cursor.fetchall()

    tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

    productos_dic = []
    for p in productos:
        precio_clp =p[5]
        producto = {
            'id_producto': p[0],
            'nombre':p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': precio_clp,
            'precio_usd': round(precio_clp / tipo_usd, 2),
            'precio_eur': round(precio_clp / tipo_eur, 2),
            'precio_ars': round(precio_clp / tipo_ars, 2),
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})



def materiales_basicos(request):
    categoria = 'Materiales Básicos'
    id_sucursal = request.session.get('id_sucursal')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s AND id_sucursal = %s', [categoria, id_sucursal])
        productos = cursor.fetchall()

    tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

    productos_dic = []
    for p in productos:
        precio_clp =p[5]
        producto = {
            'id_producto': p[0],
            'nombre':p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': precio_clp,
            'precio_usd': round(precio_clp / tipo_usd, 2),
            'precio_eur': round(precio_clp / tipo_eur, 2),
            'precio_ars': round(precio_clp / tipo_ars, 2),
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})



def tor_ancl(request):
    categoria = 'Tornillos y Anclajes'
    id_sucursal = request.session.get('id_sucursal')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s AND id_sucursal = %s', [categoria, id_sucursal])
        productos = cursor.fetchall()

    tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

    productos_dic = []
    for p in productos:
        precio_clp =p[5]
        producto = {
            'id_producto': p[0],
            'nombre':p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': precio_clp,
            'precio_usd': round(precio_clp / tipo_usd, 2),
            'precio_eur': round(precio_clp / tipo_eur, 2),
            'precio_ars': round(precio_clp / tipo_ars, 2),
            'cantidad': p[6]

        }
        productos_dic.append(producto)

    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})

def eq_medicion(request):
    categoria = 'Equipos de Medición'
    id_sucursal = request.session.get('id_sucursal')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s AND id_sucursal = %s', [categoria, id_sucursal])
        productos = cursor.fetchall()

    tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

    productos_dic = []
    for p in productos:
        precio_clp =p[5]
        producto = {
            'id_producto': p[0],
            'nombre':p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': precio_clp,
            'precio_usd': round(precio_clp / tipo_usd, 2),
            'precio_eur': round(precio_clp / tipo_eur, 2),
            'precio_ars': round(precio_clp / tipo_ars, 2),
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})



def adhesivos(request):
    categoria = 'Fijaciones y Adhesivos'
    id_sucursal = request.session.get('id_sucursal')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s AND id_sucursal = %s', [categoria, id_sucursal])
        productos = cursor.fetchall()

    tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

    productos_dic = []
    for p in productos:
        precio_clp =p[5]
        producto = {
            'id_producto': p[0],
            'nombre':p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': precio_clp,
            'precio_usd': round(precio_clp / tipo_usd, 2),
            'precio_eur': round(precio_clp / tipo_eur, 2),
            'precio_ars': round(precio_clp / tipo_ars, 2),
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})



def agregar_al_carrito(request, id_producto):
    if not request.session.get('usuario_id'):
        return redirect('iniciar_sesion')

    id_usuario = request.session.get('usuario_id')

    if request.method == 'POST':

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cantidad FROM carrito WHERE id_usuario = %s AND id_producto = %s",
                [id_usuario, id_producto]
            )
            resultado = cursor.fetchone()

            if resultado:
                nueva_cantidad = resultado[0] + 1
                cursor.execute(
                    "UPDATE carrito SET cantidad = %s WHERE id_usuario = %s AND id_producto = %s",
                    [nueva_cantidad, id_usuario, id_producto]
                )
            else:
                cursor.execute(
                    "INSERT INTO carrito (id_usuario, id_producto, cantidad) VALUES (%s, %s, 1)",
                    [id_usuario, id_producto]
                )

        if 'seguir_comprando' in request.POST:
            return redirect('home')
        

        return redirect('ver_carrito')
    
    return redirect('home')



def ver_carrito(request):
    if not request.session.get('usuario_id'):
        return redirect('iniciar_sesion')

    id_usuario = request.session['usuario_id']
    productos = []
    total = 0

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id_carrito, p.nombre, p.precio, c.cantidad, (p.precio * c.cantidad) AS total, p.id_producto
            FROM carrito c
            JOIN producto p ON p.id_producto = c.id_producto
            WHERE c.id_usuario = %s
        """, [id_usuario])

        tipo_usd, tipo_eur, tipo_ars = obtener_tipos_cambio()

        productoss = cursor.fetchall()

        for p in productoss:
            productos.append({
                'nombre': p[1],
                'precio': p[2],
                'cantidad': p[3],
                'subtotal': p[4],
                'id_producto': p[5]
            })
            total += p[4]

        divisas = {
            'total_usd': round(total / tipo_usd, 2),
            'total_eur': round(total / tipo_eur, 2),
            'total_ars': round(total / tipo_ars, 2),
        }
        
        if productos:
            request.session['carrito_id'] = productos[0]

    return render(request, 'carrito.html', {'productos': productos, 'total': total, 'divisas': divisas})



def eliminar_del_carrito(request, id_producto):
    if not request.session.get('usuario_id'):
        return redirect('iniciar_sesion')

    id_usuario = request.session['usuario_id']

    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM carrito 
            WHERE id_usuario = %s AND id_producto = %s
        """, [id_usuario, id_producto])

    return redirect('ver_carrito')




def modificar_cantidad(request, id_producto):
    if request.method == 'POST' and request.session.get('usuario_id'):
        id_usuario = request.session['usuario_id']
        cantidad = int(request.POST.get('cantidad', 1))

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE carrito SET cantidad = %s
                WHERE id_usuario = %s AND id_producto = %s
            """, [cantidad, id_usuario, id_producto])

    return redirect('ver_carrito')



def checkout(request):
    if request.session.get('admin_id'):
        return redirect('home')
    elif not request.session.get('usuario_id'):
        return redirect('iniciar_sesion')
    else: 
        if request.method == 'POST':
            metodo_entrega = request.POST.get('entrega')
        
            request.session['metodo_entrega'] = metodo_entrega
            id_sucursal = request.session.get('id_sucursal')

            return redirect('webpay')
            
        id_usuario = request.session['usuario_id']

        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT SUM(p.precio * c.cantidad) 
                    FROM carrito c
                    JOIN producto p ON p.id_producto = c.id_producto
                    WHERE c.id_usuario = %s
                """, [id_usuario])
            total = cursor.fetchone()[0]


        return render(request, 'entrega_pago.html', {'total': total})





def perfil(request):
    if not request.session.get('usuario_id') and not request.session.get('admin_id'):
        return redirect('iniciar_sesion')

    pedidos_info = []
    mensajes_dic = []
    datos_dic = {}

    if request.session.get('usuario_id'):

        id_usuario = request.session.get('usuario_id')

        with connection.cursor() as cursor:
            cursor.execute("""SELECT CONCAT(pnombre, ' ', snombre, ' ', apaterno, ' ', amaterno) AS nombre,
                                CONCAT(REPLACE(FORMAT(rut, 0), ',', '.'), '-', dv) AS rut,
                                correo
                            FROM usuario WHERE id_usuario = %s""", [id_usuario])
            datos = cursor.fetchone()

        if datos:
            datos_dic = {
                'nombre': datos[0], 'rut': datos[1], 'correo': datos[2]

            }
        else: 
            datos_dic = {}

            
        
        with connection.cursor() as cursor:
            cursor.execute("""SELECT pp.id_pedido, p.nombre, p.precio, 
                            pp.cantidad, pp.total, pp.metodo_entrega, pp.sucursal_retiro, pp.fecha
                            FROM pedido pp JOIN producto p ON pp.id_producto = p.id_producto
                            WHERE pp.id_usuario = %s""", [id_usuario])
            pedidos = cursor.fetchall()

        for p in pedidos:
            pedido = {
                'id_pedido':p[0], 'producto': p[1], 'precio': p[2], 'cantidad': p[3], 'total': p[4], 'entrega': p[5], 'sucursal': p[6], 'fecha': p[7]
            }
            pedidos_info.append(pedido)


    elif request.session.get('admin_id'):

        id_admin = request.session.get('admin_id')
        id_sucursal = request.session.get('id_sucursal')

        with connection.cursor() as cursor:
            cursor.execute("""SELECT CONCAT(a.nombre, ' ', a.snombre, ' ', a.apaterno, ' ', a.amaterno) AS nombre,
                                a.rut,
                                a.correo, 
                                s.nombre
                            FROM administrador a JOIN sucursal s ON a.id_sucursal = s.id_sucursal WHERE id = %s""", [id_admin])
            datos = cursor.fetchone()

        if datos:
            datos_dic = {
                'nombre': datos[0],
                'rut': datos[1],
                'correo': datos[2],
                'sucursal': datos[3]
            }
        else: 
            datos_dic = {}


        with connection.cursor() as cursor:
            cursor.execute("""SELECT correo, mensaje, estado, id FROM mensajes_contacto WHERE id_sucursal = %s """, [id_sucursal])
            mensajes = cursor.fetchall()

        mensajes_dic = []

        for m in mensajes:
            mensajes_dic.append({
                'correo': m[0],
                'mensaje': m[1], 
                'estado' : m[2],
                'id': m[3]

            })

        

    return render(request, 'perfil.html', {'d': datos_dic, 'mensajes': mensajes_dic, 'pedidos': pedidos_info} )






def pagar(request):
    if not request.session.get('usuario_id'):
        return redirect('iniciar_sesion')
        
    usuario_id = request.session.get('usuario_id')

    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT SUM(p.precio * c.cantidad) 
                FROM carrito c
                JOIN producto p ON p.id_producto = c.id_producto
                WHERE c.id_usuario = %s
            """, [usuario_id])
        total = cursor.fetchone()[0]
    
    if not total:
        total = 0

    
    transaction = get_webpay_transaction()

    url_return = request.build_absolute_uri(reverse('resultado_pago'))

    response = transaction.create(
        buy_order=f'orden_{int(time.time())}',
        session_id=str(usuario_id),
        amount=total,
        return_url=url_return
    )

    return render(request, 'webpay_pago.html', {
        'url_pago': response['url'],
        'token': response['token'],
    })




@csrf_exempt
def resultado_pago(request):
    token_ws = request.POST.get('token_ws') or request.GET.get('token_ws')
    if not token_ws:
        return render(request, 'entrega_pago.html',{'mensaje': f'Error procesando pago. Intente nuevamente más tarde'} )

    transaction = get_webpay_transaction()

    id_sucursal = request.session.get('id_sucursal')
    try:
        resultado = transaction.commit(token_ws)
        status = resultado['status']

        if status == 'AUTHORIZED':
            id_usuario = request.session.get('usuario_id')

            id_pedido = resultado.get('buy_order')

            with connection.cursor() as cursor:
                cursor.execute("""SELECT c.id_producto, 
                                  CONCAT(REPLACE(FORMAT(u.rut, 0), ',', '.'), '-', u.dv) AS rut, 
                                  CONCAT(u.pnombre,' ', u.apaterno, ' ', u.amaterno) AS nombre,
                                  p.precio,
                                  c.cantidad,
                                  (p.precio * c.cantidad) AS subtotal
                                  FROM carrito c JOIN usuario u ON c.id_usuario = u.id_usuario
                                  JOIN producto p ON p.id_producto = c.id_producto
                                  WHERE c.id_usuario = %s AND p.id_sucursal = %s """, [id_usuario, id_sucursal])

                productos = cursor.fetchall()

                entrega = request.session.get('metodo_entrega')

                sucursal = None

                if id_sucursal == '1' or id_sucursal == 1:
                    sucursal = 'Viña del Mar, Álvarez 1822'
                elif id_sucursal == '2' or id_sucursal == 2:
                    sucursal = 'Valparaíso, Barón 1345'
                elif id_sucursal == '3' or id_sucursal == 3:
                    sucursal = 'Santiago, Av. Grecia 12'

                for producto in productos:
                    id_producto, rut, nombre, precio, cantidad, total = producto
                    cursor.execute("""INSERT INTO pedido (id_pedido, id_usuario, id_producto, rut, nombre, precio, cantidad, total, metodo_entrega, sucursal_retiro, id_sucursal)
                                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                                      [id_pedido, id_usuario, id_producto, rut, nombre, precio, cantidad, total, entrega, sucursal, id_sucursal])
                    
                    cursor.execute("UPDATE producto SET cantidad = cantidad - %s WHERE id_producto = %s AND id_sucursal = %s", [cantidad, id_producto, id_sucursal])

            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM carrito WHERE id_usuario = %s", [id_usuario])
            
            return render(request, 'resultado_pago.html', {'resultado': resultado})
        else: 
            return render(request, 'resultado_pago.html', {'resultado': resultado})
    except Exception as e:
        return render(request, 'entrega_pago.html',{'mensaje': f'Error procesando pago: {str(e)}'} )




def contacto_usuario(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        mensaje = request.POST.get('mensaje')
        id_sucursal = request.POST.get('sucursal')
        id_usuario = request.session.get('usuario_id')

        if correo == "" or mensaje =="":
            return render(request, 'contacto.html', {'mensaje': 'Ningún campo debe estar vacío'})
        else:
            with connection.cursor() as cursor:
                cursor.execute(""" INSERT INTO mensajes_contacto (id_usuario, correo, mensaje, id_sucursal)
                                   VALUES(%s, %s, %s, %s)""", [id_usuario, correo, mensaje, id_sucursal])

            return redirect('home')
    return render(request, 'contacto.html')



def marcar_leido(request):
    id_mensaje = request.POST.get('id_mensaje')
    if id_mensaje:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE mensajes_contacto SET estado = %s WHERE id = %s", ['leído', id_mensaje])
    return redirect('perfil')
