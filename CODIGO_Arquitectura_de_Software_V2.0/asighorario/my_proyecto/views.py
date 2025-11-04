from .models import Login
from .forms import LoginForm
from django.http import HttpResponse
from functools import wraps
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json
from .models import Materia, MateriaHorario, Horario
from my_proyecto import models
from datetime import time, timedelta, datetime
import math
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django import forms
# my_proyecto/views.py
from .models import RolesPermisos, EstadoUsuario
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Usuario, Profesor  # verifica tus nombres de modelo
from .forms import ProfesorForm
import logging
# my_proyecto/views.py (imports necesarios)
from django.db import connection, transaction, IntegrityError, OperationalError
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import re
import unicodedata

logger = logging.getLogger(__name__)

def administrador_view(request):
    """
    Vista del panel administrador.
    - Verifica sesión + rol (usa request.session['username'] si está)
    - Si no hay sesión o no es admin: muestra mensaje y redirige al login
    - Si es admin: carga profesores y renderiza administrador.html
    """

    # 1) Obtener username desde la sesión
    username = request.session.get('username')
    if not username:
        # No hay usuario en sesión -> negar acceso
        messages.error(request, "Acceso denegado. No has iniciado sesión.")
        return redirect(reverse('my_proyecto:login'))

    # 2) Consultar rol del usuario en la base de datos (tabla Usuario -> RolesPermisos)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT r.Nombre
                FROM Usuario u
                LEFT JOIN RolesPermisos r ON u.RolId = r.Id
                WHERE u.Username = %s
                LIMIT 1
            """, [username])
            row = cursor.fetchone()
            rol_nombre = row[0] if row and row[0] is not None else None
    except OperationalError:
        logger.exception("Error de conexión a la BD al consultar rol del usuario")
        messages.error(request, "Error de conexión a la base de datos. Intenta más tarde.")
        # Opcional: redirigir a index o login
        return redirect(reverse('my_proyecto:login'))
    except Exception:
        logger.exception("Error inesperado al consultar rol de usuario")
        messages.error(request, "Ocurrió un error. Contacta al administrador.")
        return redirect(reverse('my_proyecto:login'))

    # 3) Validar que el rol sea administrador (admite distintas formas de nombre)
    if not rol_nombre or rol_nombre.strip().lower() not in ['administrador', 'administrador del sistema']:
        # No es administrador -> acceso denegado con mensaje
        messages.error(request, "Acceso denegado. No eres administrador.")
        return redirect(reverse('my_proyecto:login'))

    # 4) Si es admin, continuar cargando datos para el template
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Id, Nombre FROM Profesor")
            filas = cursor.fetchall()
    except OperationalError:
        logger.exception("Error de conexión a la BD al obtener profesores")
        messages.error(request, "Error de conexión a la base de datos. Intenta más tarde.")
        return redirect(reverse('my_proyecto:login'))
    except Exception:
        logger.exception("Error inesperado al obtener profesores")
        messages.error(request, "Ocurrió un error al cargar la información.")
        return redirect(reverse('my_proyecto:login'))

    # Mapear filas a lista de diccionarios simple para el template
    profesores = [{'id': f[0], 'nombre': f[1]} for f in filas]

    # Renderizar template (aquí usamos username para mostrar 'Bienvenido')
    response = render(request, 'my_proyecto/administrador.html', {
        'profesores': profesores,
        'username': username,
    })

    # 5) Limpiar flag open_form (si fue puesto por una acción previa)
    try:
        if request.session.get('open_form'):
            request.session.pop('open_form')
    except Exception:
        # No bloquear la vista por un problema de sesión
        logger.exception("No se pudo limpiar request.session['open_form']")

    return response


def vista_inicio(request):
    return render(request, 'index.html') # Asume que tienes un template llamado inicio.html

def index(request):
    return render(request, 'my_proyecto/index.html')

def login_list(request):
    return HttpResponse("Login List Page")

@csrf_exempt
def login_api_admin(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    username = (request.POST.get("username") or "").strip().lower()
    password = (request.POST.get("password") or "").strip()

    if not username or not password:
        return JsonResponse({"success": False, "error": "Usuario y contraseña requeridos"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.Id, u.Username, u.Password, rp.Nombre AS Rol
            FROM Usuario u
            JOIN RolesPermisos rp ON u.RolId = rp.Id
            WHERE u.Username = %s
            LIMIT 1
        """, [username])
        row = cursor.fetchone()

    if not row:
        return JsonResponse({"success": False, "error": "Usuario no encontrado"}, status=401)

    user_id, user_name, stored_password, user_rol = row

    if not check_password(password, stored_password):
        return JsonResponse({"success": False, "error": "Contraseña incorrecta"}, status=401)

    if user_rol.strip().lower() not in ['administrador', 'administrador del sistema']:
        return JsonResponse({"success": False, "error": "Acceso denegado. No eres administrador."}, status=403)

    # Guardar sesión
    request.session['user_id'] = user_id
    request.session['username'] = user_name
    request.session['user_role'] = user_rol

    redirect_url = reverse('my_proyecto:administrador')
    return JsonResponse({"success": True, "redirect": redirect_url})


def vista_administrador(request):
    return render(request, 'my_proyecto/administrador.html')

def administrador(request):
    if not request.session.get('user_id'):
        messages.info(request, "Debes iniciar sesión como administrador.")
        return redirect('my_proyecto:login')  # Asegúrate de que 'login' esté definido en urls.py

    rol = (request.session.get('user_role') or "").strip().lower()
    if rol != 'administrador':
        messages.error(request, "Acceso denegado. No eres administrador.")
        return render(request, 'my_proyecto/index.html')  # O redirige a una vista segura

    context = {'username': request.session.get('username')}
    return render(request, 'my_proyecto/administrador.html', context)

def logout_view(request):
    request.session.flush()  # Elimina toda la sesión
    return redirect('my_proyecto:index')  # Redirige a index.html


def maestros(request):
    return render(request, 'my_proyecto/maestros.html')

def menu_profesor(request):
    profesor_id = request.session.get('profesor_id')
    if not profesor_id:
        messages.error(request, "Debes iniciar sesión como profesor.")
        return redirect('my_proyecto:index')   # <-- cambiar aquí

    return horario_profesor(request, profesor_id)

@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    usuario = (request.POST.get("usuario") or "").strip().lower()
    contrasena = (request.POST.get("contrasena") or "").strip()

    if not usuario or not contrasena:
        return JsonResponse({"success": False, "error": "Usuario y contraseña requeridos"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.Id, u.Username, u.Password, rp.Nombre AS Rol
            FROM Usuario u
            JOIN RolesPermisos rp ON u.RolId = rp.Id
            WHERE u.Username = %s
            LIMIT 1
        """, [usuario])
        row = cursor.fetchone()

    if not row:
        return JsonResponse({"success": False, "error": "Usuario no encontrado"}, status=401)

    user_id, username, stored_password, rol_nombre = row

    if not check_password(contrasena, stored_password):
        return JsonResponse({"success": False, "error": "Contraseña incorrecta"}, status=401)

    request.session['user_id'] = user_id
    request.session['username'] = username
    request.session['user_role'] = rol_nombre

    rol_lower = rol_nombre.lower()
    if "administrador" in rol_lower:
        return JsonResponse({"success": True, "redirect": reverse('my_proyecto:administrador')})
    elif "profesor" in rol_lower:
        return JsonResponse({"success": True, "redirect": reverse('my_proyecto:menu_de_profesor')})
    else:
        return JsonResponse({"success": False, "error": "Rol no autorizado"}, status=403)


def signup(request):
    form = LoginForm()  # <-- reiniciar formulario vacío
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario_nombre = form.cleaned_data['usuario']
            contrasena = form.cleaned_data['contrasena']
            rol = form.cleaned_data['rol']
            especialidad = form.cleaned_data['especialidad'] or 'N/A'
            usuario_email = f'{usuario_nombre}@ejemplo.com'

            with connection.cursor() as cursor:
                # 1. Insertar en Usuario
                cursor.execute("""
                    INSERT INTO Usuario (Nombre, Email, Rol)
                    VALUES (%s, %s, %s)
                """, [usuario_nombre, usuario_email, rol])
                cursor.execute("SELECT LAST_INSERT_ID()")
                usuario_id = cursor.fetchone()[0]

                # 2. Insertar en Login
                cursor.execute("""
                    INSERT INTO Login (UsuarioId, Usuario, Contrasena)
                    VALUES (%s, %s, %s)
                """, [usuario_id, usuario_nombre, contrasena])
                hashed = make_password(contrasena)

                # 3. Insertar en tabla correspondiente
                if rol == 'Profesor':
                    cursor.execute("""
                        INSERT INTO Profesor (Nombre, Especialidad, UsuarioId)
                        VALUES (%s, %s, %s)
                    """, [usuario_nombre, especialidad, usuario_id])
                else:
                    cursor.execute("""
                        INSERT INTO Administrador (UsuarioId)
                        VALUES (%s)
                    """, [usuario_id])

            messages.success(request, f"Registro exitoso como {rol.lower()}")
            return redirect('my_proyecto:index')
            
    else:
        form = LoginForm()
    return render(request, 'my_proyecto/signup.html', {'form': form})

# Si tienes modelos ORM para Login/Usuario:
try:
    from .models import Login, Usuario
except Exception:
    Login = None
    Usuario = None

@csrf_exempt
def login_api_profesor(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    usuario = (request.POST.get("usuario") or "").strip().lower()
    contrasena = (request.POST.get("contrasena") or "").strip()

    if not usuario or not contrasena:
        return JsonResponse({"success": False, "error": "Usuario y contraseña requeridos"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.Id, u.Username, u.Password, rp.Nombre AS Rol
            FROM Usuario u
            JOIN RolesPermisos rp ON u.RolId = rp.Id
            WHERE u.Username = %s
            LIMIT 1
        """, [usuario])
        row = cursor.fetchone()

    if not row:
        return JsonResponse({"success": False, "error": "Usuario no encontrado"}, status=401)

    user_id, user_name, stored_password, user_rol = row

    if not check_password(contrasena, stored_password):
        return JsonResponse({"success": False, "error": "Contraseña incorrecta"}, status=401)

    if "profesor" not in (user_rol or "").strip().lower():
        return JsonResponse({"success": False, "error": "Acceso denegado. No eres profesor."}, status=403)

    request.session['user_id'] = user_id
    request.session['username'] = user_name
    request.session['user_role'] = user_rol

    with connection.cursor() as cursor:
        cursor.execute("SELECT Id FROM Profesor WHERE UsuarioId = %s LIMIT 1", [user_id])
        prof_row = cursor.fetchone()

    if not prof_row:
        return JsonResponse({"success": False, "error": "No se encontró el perfil de profesor"}, status=404)

    profesor_id = prof_row[0]
    request.session['profesor_id'] = profesor_id

    redirect_url = reverse('my_proyecto:menu_profesor')
    return JsonResponse({"success": True, "redirect": redirect_url})

#CREAR VISTA MENU_PROFESORES QUE USE LA SESION
def menu_profesor(request):
    profesor_id = request.session.get('profesor_id')
    if not profesor_id:
        messages.error(request, "Debes iniciar sesión como profesor.")
        return redirect('my_proyecto:login')
    return horario_profesor(request, profesor_id)
# Agregar Profesor
logger = logging.getLogger(__name__)

def obtener_id_por_nombre(tabla, campo_nombre, valor):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT Id FROM {tabla} WHERE {campo_nombre} = %s", [valor])
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
#///////////////********************************//////////////////////////////////////////////////#
# utilitarios
def slugify_basic(s):
    """Simplificación: convierte a ascii, minuscula y reemplaza espacios por punto."""
    if not s:
        return ''
    # quitar tildes y normalizar
    s_norm = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s_norm = re.sub(r'[^a-zA-Z0-9\s]', '', s_norm)
    return re.sub(r'\s+', '.', s_norm.strip()).lower()

def generar_email(nombre, ap_pat, num_empleado):
    userpart = f"{slugify_basic(nombre)}.{slugify_basic(ap_pat)}.{num_empleado}"
    return f"{userpart}@gmail.com"

def generar_username(nombre, ap_pat, profesor_id):
    return f"{slugify_basic(nombre)}.{slugify_basic(ap_pat)}.{profesor_id}"

def generar_password_plain(ap_pat, num_empleado):
    # ejemplo: ApPat + NumEmpleado
    base = f"{slugify_basic(ap_pat)}{num_empleado}"
    # si quieres más seguridad, podrías añadir un sufijo aleatorio y luego enviar al profesor
    return base

# VIEW
def agregar_profesor(request):
    if request.method == 'GET':
        # preparar selects para estados y aulas
        with connection.cursor() as cursor:
            cursor.execute("SELECT Id, Estado FROM Estados")
            estados = cursor.fetchall()
            cursor.execute("SELECT Id, NombreAula FROM Aulas")
            aulas = cursor.fetchall()
        return render(request, 'my_proyecto/administrador.html', {
            'estados': estados,
            'aulas': aulas
        })

    # POST: procesar registro
    nombre = request.POST.get('nombre', '').strip()
    ap_pat = request.POST.get('ap_pat', '').strip()
    ap_mat = request.POST.get('ap_mat', '').strip()
    num_empleado = request.POST.get('num_empleado', '').strip()
    direccion = request.POST.get('direccion', '').strip()
    email_input = request.POST.get('email', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    fecha_ingreso = request.POST.get('fecha_ingreso') or None  # formato YYYY-MM-DD
    estado_id = request.POST.get('estado_id') or 1
    especialidad = request.POST.get('especialidad', '').strip()
    aula_id = request.POST.get('aula_id') or None

    #Validar conexión con base de datos antes del registro
    try:
        connection.ensure_connection()
    except Exception:
        messages.error(request, "Error de conexión con la base de datos. Intenta más tarde.")
        request.session['open_form'] = 'agregarProfesorForm'
        return redirect(reverse('my_proyecto:administrador'))

    # validaciones mínimas
    if not nombre or not ap_pat or not num_empleado:
        messages.error(request, "Nombre, Apellido paterno y Num. Empleado son obligatorios.")
        return redirect(reverse('my_proyecto:agregar_profesor'))
    # Validar campos requeridos
    if not all([nombre, ap_pat or email_generado, num_empleado, especialidad]):
        messages.error(request, "Todos los campos obligatorios deben completarse.")
        request.session['open_form'] = 'agregarProfesorForm'
        return redirect(reverse('my_proyecto:agregar_profesor'))
    # Validar solo letras en campos de texto
    if not all(re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$', campo or '') 
               for campo in [nombre, ap_pat, ap_mat, especialidad]):
        messages.error(request, "Los campos de texto solo pueden contener letras y espacios.")
        request.session['open_form'] = 'agregarProfesorForm'
        return redirect(reverse('my_proyecto:administrador'))

    # generar email si no lo dieron
    if not email_input:
        email_generado = generar_email(nombre, ap_pat, num_empleado)
    else:
        email_generado = email_input.lower()
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email_generado):
        messages.error(request, "El correo electrónico no tiene un formato válido.")
        request.session['open_form'] = 'agregarProfesorForm'
        return redirect(reverse('my_proyecto:administrador'))
    # Validar si el número de empleado ya existe
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Profesor WHERE NumEmpleado = %s", [num_empleado])
        existe = cursor.fetchone()[0]
        if existe > 0:
            messages.error(request, f"Número de empleado '{num_empleado}' ya existe. Por favor indique otro.")
            # Mantener el formulario abierto
            request.session['open_form'] = 'agregarProfesorForm'
            # Recargar la misma vista sin redireccionar
            with connection.cursor() as cursor:
                cursor.execute("SELECT Id, Estado FROM Estados")
                estados = cursor.fetchall()
                cursor.execute("SELECT Id, NombreAula FROM Aulas")
                aulas = cursor.fetchall()
            return render(request, 'my_proyecto/administrador.html', {
                'estados': estados,
                'aulas': aulas,
                'username': request.session.get('username', 'Admin'),
            })
    # Validar si el correo electrónico ya existe
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Profesor WHERE Email = %s", [email_generado])
        existe_email = cursor.fetchone()[0]
        if existe_email > 0:
            messages.error(request, f"El correo electrónico '{email_generado}' ya existe. Por favor indica otro.")
            request.session['open_form'] = 'agregarProfesorForm'
            with connection.cursor() as cursor:
                cursor.execute("SELECT Id, Estado FROM Estados")
                estados = cursor.fetchall()
                cursor.execute("SELECT Id, NombreAula FROM Aulas")
                aulas = cursor.fetchall()
            return render(request, 'my_proyecto/administrador.html', {
                'estados': estados,
                'aulas': aulas,
                'username': request.session.get('username', 'Admin'),
            })
    # Transacción: insertar Profesor, luego crear Usuario, luego actualizar Profesor.UsuarioId
    start_time = time.time()
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Profesor WHERE NumEmpleado = %s", [num_empleado])
                existe = cursor.fetchone()[0]
                if existe > 0:
                    messages.error(request, f"Ya existe un profesor con el número de empleado '{num_empleado}'.")
                    return redirect(reverse('my_proyecto:agregar_profesor'))
                # 1) Insertar en Profesor (sin UsuarioId)
                cursor.execute("""
                    INSERT INTO Profesor
                      (Nombre, ApPat, ApMat, NumEmpleado, Direccion, Email, Telefono, FechaIngreso, EstadoId, Especialidad, UsuarioId, AulaId)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL,%s)
                """, [nombre, ap_pat, ap_mat, num_empleado, direccion, email_generado, telefono, fecha_ingreso, estado_id, especialidad, aula_id])
                cursor.execute("SELECT LAST_INSERT_ID();")
                profesor_id = cursor.fetchone()[0]

                # 2) Generar usuario y contraseña
                username = generar_username(nombre, ap_pat, profesor_id)
                password_plain = generar_password_plain(ap_pat, num_empleado)
                password_hashed = make_password(password_plain, hasher='pbkdf2_sha256')

                # 3) Insertar en Usuario (ajusta RolId por el id real de Profesor en tu RolesPermisos)
                # Busca el RolId de 'Profesor' (si existe)
                cursor.execute("SELECT Id FROM RolesPermisos WHERE Nombre LIKE %s LIMIT 1", ['%Profesor%'])
                row = cursor.fetchone()
                rol_id = row[0] if row else None
                # Si no existe rol, puedes usar NULL o un id por defecto
                cursor.execute("""
                    INSERT INTO Usuario (FechaAlta, Username, Password, RolId, EstadoUsId)
                    VALUES (CURDATE(), %s, %s, %s, %s)
                """, [username, password_hashed, rol_id, 1])
                cursor.execute("SELECT LAST_INSERT_ID();")
                usuario_id = cursor.fetchone()[0]

                # 4) Actualizar Profesor para enlazar UsuarioId
                cursor.execute("UPDATE Profesor SET UsuarioId = %s WHERE Id = %s", [usuario_id, profesor_id])

        # fuera de la transacción: enviar correo de confirmación
        asunto = "Registro de cuenta - Sistema de Horarios"
        mensaje = (
            f"Hola {nombre} {ap_pat},\n\n"
            f"Se ha creado tu cuenta en el sistema.\n\n"
            f"Username: {username}\n"
            f"Password (temporal): {password_plain}\n\n"
            "Por favor cambia tu contraseña al iniciar sesión.\n\n"
            "Saludos."
        )
        # Enviar a la dirección de confirmación solicitada (cuapantecatl1@gmail.com)
        try:
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cuapantecatl1@gmail.com'],  # pedido explícitamente
                fail_silently=False,
            )
            # (Opcional) enviar también al email generado del profesor:
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_generado],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Fallo al enviar correo de confirmación")

        elapsed = time.time() - start_time
        if elapsed > 2.0:
            logger.warning(f"Inserción de profesor tomó {elapsed:.2f}s (>2s)")

        messages.success(request, "Profesor registrado correctamente.")
        request.session.pop('open_form', None)
        messages.success(request, "Profesor registrado correctamente. Se ha enviado confirmación por correo.")
        return redirect(reverse('my_proyecto:administrador'))

    except IntegrityError:
        messages.error(request, "El email o número de empleado ya existen. No se pudo crear el profesor.")
        return redirect(reverse('my_proyecto:agregar_profesor'))

    except OperationalError:
        messages.error(request, "Error de conexión a la base de datos. Intenta más tarde.")
        return redirect(reverse('my_proyecto:agregar_profesor'))

    except Exception as e:
        logger.exception("Error al crear profesor")
        messages.error(request, "Ocurrió un error inesperado. Contacta al administrador.")
        return redirect(reverse('my_proyecto:agregar_profesor'))

def poblar_catalogos(request):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO RolesPermisos (Nombre) VALUES ('Administrador'), ('Administrador del sistema'), ('Profesor'), ('Profesor académico')")
        cursor.execute("INSERT INTO EstadoUsuario (EstadoUs) VALUES ('Activo'), ('Inactivo'), ('Bloqueado')")
        cursor.execute("INSERT INTO Estados (Estado) VALUES ('Activo'), ('Inactivo'), ('Vacaciones'), ('Licencia_Medica'), ('Jubilado')")
        # Puedes agregar aulas aquí también si lo deseas
    return HttpResponse("Catálogos insertados correctamente.")

def gestionar_profesores(request):
    profesores = Profesor.objects.all()
    return render(request, 'mi_app/gestionar_profesores.html', {'profesores': profesores})

# Buscar Profesor
def buscar_profesor(request):
    profesores = Profesor.objects.all()
    id_buscar = request.GET.get('id')
    nombre_buscar = request.GET.get('nombre')

    # Filtrar por ID si se ingresó
    if id_buscar:
        profesores = profesores.filter(id=id_buscar)

    # Filtrar por nombre si se ingresó
    if nombre_buscar:
        profesores = profesores.filter(nombre__icontains=nombre_buscar)

    # Para el modal de edición
    all_materias = Materia.objects.all()

    return render(request, 'administrador.html', {
        'profesores': profesores,
        'all_materias': all_materias
    })

# Editar Profesor
def editar_profesor(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    if request.method == "POST":
        profesor.nombre = request.POST['nombre']
        profesor.especialidad = request.POST['especialidad']
        profesor.save()

        # Actualizar materias asignadas
        materias_ids = request.POST.getlist('materias')
        profesor.materias.set(Materia.objects.filter(id__in=materias_ids))

        return redirect('panel_admin')


# Eliminar Profesor
def eliminar_profesor(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    profesor.delete()
    return redirect('panel_admin')

# Agregar Materia
def agregar_materia(request):
    if request.method == "POST":
        nombre = request.POST['nombre_materia']
        aula = request.POST['aula']
        Materia.objects.create(nombre=nombre, aula=aula)
        return redirect('panel_admin')

# Agregar Horario
def agregar_horario(request):
    if request.method == "POST":
        dia = request.POST['dia']
        inicio = request.POST['horario_inicio']
        fin = request.POST['hora_fin']
        Horario.objects.create(dia=dia, horario_inicio=inicio, hora_fin=fin)
        return redirect('panel_admin')
    
def panel_admin(request):
    all_materias = Materia.objects.all()  # Obtenemos todas las materias
    return render(request, 'admin_panel.html', {'all_materias': all_materias})

# HORARIO PROFESOR
# Configuración: horario visible y tamaño de slot en minutos
# Configuración de slots Configuración
SLOT_MINUTES = 30
# Asegúrate que los nombres aquí coincidan exactamente con los valores en la columna DiasLab.DiaL
DAY_ORDER = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']  
# Si en tu BD usas 'Miercoles' sin tilde, cámbialo por 'Miercoles' aquí.
START_TIME = time(7,0)
END_TIME = time(21,0)

def _time_to_minutes(t):
    return t.hour*60 + t.minute

def _minutes_to_time(minutes):
    h = minutes // 60
    m = minutes % 60
    return time(h, m)

def horario_profesor(request, profesor_id):
    # Consulta: obtener clases para el profesor
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT m.Id as materia_id, m.Nombre as materia,
               mh.HorarioId as horario_id,
               h.DiaId,
               d.DiaL as dia,
               hs.Hora as inicio,
               he.Hora as fin,
               a.Id as aula_id, a.NombreAula as aula, a.Edificio as edificio,
               mg.GrupoId as grupo_id
        FROM Materia m
        JOIN MateriaHorario mh ON mh.MateriaId = m.Id
        JOIN Horario h ON h.Id = mh.HorarioId
        JOIN DiasLab d ON d.Id = h.DiaId
        JOIN Horas hs ON hs.Id = h.HorarioInicioId
        JOIN Horas he ON he.Id = h.HoraFinId
        LEFT JOIN Aulas a ON a.Id = mh.AulaId
        LEFT JOIN MateriaGrupo mg ON mg.MateriaId = m.Id
        WHERE m.ProfesorId = %s
        ORDER BY d.Id, hs.Hora
        """, [profesor_id])
        cols = [c[0] for c in cursor.description]
        raw_rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        
    # Convertir y normalizar filas
    clases = []
    for r in raw_rows:
        # r['inicio'] y r['fin'] pueden ser str '08:00:00' o datetime.time
        inicio = r.get('inicio')
        fin = r.get('fin')
        if isinstance(inicio, str):
            inicio = datetime.strptime(inicio, "%H:%M:%S").time()
        if isinstance(fin, str):
            fin = datetime.strptime(fin, "%H:%M:%S").time()
        dur_minutes = _time_to_minutes(fin) - _time_to_minutes(inicio)
        clases.append({
            'materia_id': r.get('materia_id'),
            'materia': r.get('materia'),
            'horario_id': r.get('horario_id'),
            'dia': r.get('dia'),
            'diaId': r.get('DiaId'),
            'inicio': inicio,
            'fin': fin,
            'dur_minutes': dur_minutes,
            'aula': r.get('aula'),
            'edificio': r.get('edificio'),
            'grupo_id': r.get('grupo_id'),
        })

    # Crear slots
    start_min = _time_to_minutes(START_TIME)
    end_min = _time_to_minutes(END_TIME)
    slots = []
    for m in range(start_min, end_min, SLOT_MINUTES):
        slots.append(_minutes_to_time(m))

    # Inicializar grid
    grid = {day: [None]*len(slots) for day in DAY_ORDER}

    # Rellenar grid
    for clase in clases:
        day = clase['dia']
        # Normalizar nombre de día si BD devuelve 'Martes' y DAY_ORDER usa 'Martes' OK.
        if day not in DAY_ORDER:
            # intentar normalizar acentos comunes
            alt_day = day.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
            matches = [d for d in DAY_ORDER if d.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u') == alt_day]
            if matches:
                day = matches[0]
            else:
                # día no contemplado (p. ej. 'Sábado') -> ignorar
                continue

        inicio_min = _time_to_minutes(clase['inicio'])
        fin_min = _time_to_minutes(clase['fin'])
        start_idx = (inicio_min - start_min) // SLOT_MINUTES
        if start_idx < 0 or start_idx >= len(slots):
            # fuera del rango de visualización
            continue
        span = max(1, math.ceil((fin_min - inicio_min) / SLOT_MINUTES))
        # Colocar y marcar ocupadas
        grid[day][start_idx] = {'clase': clase, 'rowspan': span}
        for i in range(1, span):
            if start_idx + i < len(slots):
                grid[day][start_idx + i] = 'OCUPADO'

    # Construir filas ordenadas (cada fila: slot_time + lista de cells por día)
    rows = []
    for idx, slot in enumerate(slots):
        cells = [grid[d][idx] for d in DAY_ORDER]
        rows.append({'slot_time': slot, 'cells': cells})

    # Datos profesor (simple)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Id, Nombre, ApPat, ApMat, NumEmpleado, Direccion, Email, Telefono,
                   FechaIngreso, EstadoId, Especialidad, UsuarioId, AulaId
            FROM Profesor
            WHERE Id = %s
        """, [profesor_id])
        prof_row = cursor.fetchone()
        if prof_row:
            cols = [desc[0] for desc in cursor.description]
            profesor = dict(zip(cols, prof_row))
        else:
            profesor = None

    # Depuración: imprime cuántas clases y algún detalle (puedes quitar estos print más tarde)
    print("DEBUG profesor:", profesor)
    print("DEBUG clases:", len(clases))
    print("DEBUG rows:", len(rows))

    for c in clases:
        print(f"DEBUG clase: {c['materia']} dia={c['dia']} {c['inicio']} - {c['fin']} span={(c['dur_minutes']/SLOT_MINUTES)}")

    context = {
        'profesor': profesor,
        'day_order': DAY_ORDER,
        'rows': rows,
        'slot_minutes': SLOT_MINUTES,
    }
    return render(request, 'my_proyecto/menu_de_profesores.html', context)

def cerrar_sesion(request):
    request.session.flush()  # Elimina toda la sesión
    return redirect('my_proyecto:index')  # Asegúrate que 'index' esté definido en urls.py

def limpiar_open_form(request):
    if request.method == 'POST':
        request.session.pop('open_form', None)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'invalid'}, status=400)

