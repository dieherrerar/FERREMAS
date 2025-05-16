from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
import bcrypt
from django.http import HttpResponse

def add_cliente(request):
    if request.method == 'POST':
        pnombre = request.POST.get('pnombre')
        snombre = request.POST.get('snombre')
        apaterno = request.POST.get('apaterno')
        amaterno = request.POST.get('amaterno')
        rut = request.POST.get('rut')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        contrasena2 = request.POST.get('contrasena2')

        datos_formulario = {
            'pnombre': pnombre,
            'snombre': snombre,
            'apaterno': apaterno,
            'amaterno': amaterno,
            'rut': rut,
            'correo': correo,
        }


        if pnombre=="" or snombre=="" or apaterno=="" or amaterno=="" or rut=="" or correo=="" or contrasena=="" or contrasena2=="":
            return render(request, 'registro.html', {'mensaje': 'Ningún campo debe estar vacío', 'datos': datos_formulario})
        else: 
            if contrasena == contrasena2:
                if contrasena and contrasena2 and (len(contrasena) < 8 or len(contrasena) > 25 or len(contrasena2) < 8 or len(contrasena2) > 25):
                    return render(request, 'registro.html', {'mensaje': 'Las contraseñas deben tener minimo 8 caracteres y máximo 25', 'datos': datos_formulario})
                else: 
                    with connection.cursor() as cursor:
                        cursor.execute('SELECT COUNT(*) FROM usuario WHERE rut = %s', [rut])
                        rut_existe = cursor.fetchone()[0]

                        cursor.execute('SELECT COUNT(*) FROM usuario WHERE correo = %s', [correo] )
                        correo_existe = cursor.fetchone()[0]
                    
                    if rut_existe == 0 and correo_existe == 0:
                        hashed_pw = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        try: 
                            with connection.cursor() as cursor:
                                sql = """
                                    INSERT INTO usuario (pnombre, snombre, apaterno, amaterno, rut, correo, contrasena)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """
                                cursor.execute(sql, [pnombre, snombre, apaterno, amaterno, rut, correo, hashed_pw])
                
                            return redirect('home')
                        except IntegrityError as e:
                            return render(request, 'registro.html', {'mensaje': 'Error al registrar el cliente, por favor intente de nuevo', 'datos': datos_formulario})
                    else:
                        return render(request, 'registro.html', {'mensaje':'El RUT o el correo ya se encuentran registrados', 'datos': datos_formulario})

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

        datos_formulario = {
            'nombre': nombre,
            'descripcion': descripcion,
            'marca': marca,
            'precio': precio,
            'cantidad': cantidad,
        }


        if nombre=="" or descripcion=="" or categoria=="" or marca=="" or precio=="" or cantidad=="":
            return render(request, 'add_producto.html', {'mensaje': 'Ningún campo debe estar vacío', 'datos': datos_formulario})
        else: 
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO producto (nombre, descripcion, categoria, marca, precio, cantidad)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, [nombre, descripcion, categoria, marca, precio, cantidad])
        
            return redirect('home')

    return render(request, 'add_producto.html')


def modificar_prod(request, id_producto):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        marca = request.POST.get('marca')
        precio = request.POST.get('precio')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE producto
                SET nombre = %s, descripcion = %s, precio = %s, marca = %s, categoria = %s
                WHERE id_producto = %s
            """, [nombre, descripcion, precio, marca, categoria, id_producto])
        
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

    if request.session.get('usuario_id'):
        nombre = request.session.get('nombre_usuario')
    elif request.session.get('admin_id'):
        nombre = request.session.get('admin_name')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id_producto, nombre, descripcion, categoria, marca, precio, cantidad FROM producto")
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'id_producto':p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': p[5],
            'cantidad': p[6]

        }
        productos_dic.append(producto)

    return render(request, 'home.html', {'productos': productos_dic, 'nombre': nombre})



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
            contrasena_hash = admin[7].encode('utf-8')
            if bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash):
                request.session['admin_id'] = admin_id
                request.session['admin_name'] = admin_name
                return redirect('home')
            else:
                return render(request, 'admin_login.html', {'error': 'Datos ingresados son incorrectos'})
        else:
            return render(request, 'admin_login.html', {'error': 'Datos ingresados son incorrectos'})
    
    return render(request, 'admin_login.html')



def herr_manuales(request):
    categoria = 'Herramientas Manuales'
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s', [categoria])
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'id_producto':p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': p[5],
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})

def eq_seguridad(request):
    categoria = 'Equipos de Seguridad'
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s', [categoria])
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'id_producto':p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': p[5],
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})

def materiales_basicos(request):
    categoria = 'Materiales Básicos'
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s', [categoria])
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'id_producto':p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': p[5],
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})

def tor_ancl(request):
    categoria = 'Tornillos y Anclajes'
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s', [categoria])
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'id_producto':p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': p[5],
            'cantidad': p[6]

        }
        productos_dic.append(producto)

    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})

def eq_medicion(request):
    categoria = 'Equipos de Medición'
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s', [categoria])
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'id_producto':p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': p[5],
            'cantidad': p[6]

        }
        productos_dic.append(producto)
    
    return render(request, 'productos.html', {'productos': productos_dic, 'categoria': categoria})


def adhesivos(request):
    categoria = 'Fijaciones y Adhesivos'
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM producto WHERE categoria = %s', [categoria])
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'id_producto':p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'categoria': p[3],
            'marca': p[4],
            'precio': p[5],
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
            SELECT p.nombre, p.precio, c.cantidad, (p.precio * c.cantidad) AS total, p.id_producto
            FROM carrito c
            JOIN producto p ON p.id_producto = c.id_producto
            WHERE c.id_usuario = %s
        """, [id_usuario])

        productoss = cursor.fetchall()

        for p in productoss:
            productos.append({
                'nombre': p[0],
                'precio': p[1],
                'cantidad': p[2],
                'subtotal': p[3],
                'id_producto': p[4]
            })
            total += p[3]

    return render(request, 'carrito.html', {'productos': productos, 'total': total})


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
