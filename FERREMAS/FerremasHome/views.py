from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
import bcrypt

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
                        return render(request, 'registro.html', {'mensaje':'El RUT o el correo ya se encuentran registrados,', 'datos': datos_formulario})

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






def iniciar_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        with connection.cursor() as cursor:
            cursor.execute (" SELECT * FROM usuario WHERE correo = %s", [correo])
            usuario = cursor.fetchone()
        if usuario:
            usuario_id=usuario[0]
            contrasena_hash=usuario[7].encode('utf-8')
            if bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash):
                request.session['usuario_id'] = usuario_id
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Datos ingresados son incorrectos'})
        else:
            return render(request, 'login.html', {'error': 'Datos ingresados son incorrectos'})
    return render(request, 'login.html')



def home(request):

    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre, descripcion, categoria, marca, precio, cantidad FROM producto")
        productos = cursor.fetchall()

    productos_dic = []
    for p in productos:
        producto = {
            'nombre': p[0],
            'descripcion': p[1],
            'categoria': p[2],
            'marca': p[3],
            'precio': p[4],
            'cantidad': p[5]

        }
        productos_dic.append(producto)

    return render(request, 'home.html', {'productos': productos_dic})


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
            contrasena_hash = admin[7].encode('utf-8')
            if bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash):
                request.session['admin_id'] = admin_id
                return redirect('home')
            else:
                return render(request, 'admin_login.html', {'error': 'Datos ingresados son incorrectos'})
        else:
            return render(request, 'admin_login.html', {'error': 'Datos ingresados son incorrectos'})
    
    return render(request, 'admin_login.html')