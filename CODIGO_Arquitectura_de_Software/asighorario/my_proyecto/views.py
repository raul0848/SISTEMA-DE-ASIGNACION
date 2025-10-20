from django.shortcuts import get_object_or_404
from .models import Login
from .forms import LoginForm
from django.http import HttpResponse
from django.db import connection
from functools import wraps
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json
from .models import Usuario, Profesor, Materia, MateriaHorario, Horario
from .models import Materia
from my_proyecto import models
from datetime import time, timedelta, datetime
import math
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django import forms
# my_proyecto/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError, transaction, OperationalError
from django.contrib import messages
from django.contrib.auth.hashers import make_password  # usa pbkdf2_sha256 por defecto en settings
from .forms import ProfesorForm
from .models import RolesPermisos, EstadoUsuario
import logging

logger = logging.getLogger(__name__)

def administrador_view(request):
    # obtener profesores (tu código puede usar cursor o ORM)
    with connection.cursor() as cursor:
        cursor.execute("SELECT Id, Nombre FROM Profesor")
        filas = cursor.fetchall()
    # mapea filas a objetos simples para template (opcional)
    profesores = []
    for f in filas:
        profesores.append({'id': f[0], 'nombre': f[1]})
    # obtener username de sesión o request.user
    username = request.session.get('username', 'Admin')

    # renderizar
    response = render(request, 'my_proyecto/administrador.html', {
        'profesores': profesores,
        'username': username,
    })

    # limpiar flag open_form para no reabrir eternamente
    try:
        if request.session.get('open_form'):
            request.session.pop('open_form')
    except Exception:
        pass

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

def agregar_profesor(request):
    if request.session.get('rol') not in ['Administrador', 'Administrador del sistema']:
        return redirect('my_proyecto:index')

    if request.method == 'POST':
        # Datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')
        rol_nombre = request.POST.get('rol_nombre')
        estado_usuario_nombre = request.POST.get('estado_usuario_nombre')

        nombre = request.POST.get('nombre')
        ap_pat = request.POST.get('ap_pat')
        ap_mat = request.POST.get('ap_mat')
        num_empleado = request.POST.get('num_empleado')
        direccion = request.POST.get('direccion')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        fecha_ingreso = request.POST.get('fecha_ingreso')
        estado_profesor_nombre = request.POST.get('estado_profesor_nombre')
        especialidad = request.POST.get('especialidad')
        aula_nombre = request.POST.get('aula_nombre')

        # Convertir nombres en IDs
        rol_id = obtener_id_por_nombre("RolesPermisos", "Nombre", rol_nombre)
        estado_usuario_id = obtener_id_por_nombre("EstadoUsuario", "EstadoUs", estado_usuario_nombre)
        estado_id = obtener_id_por_nombre("Estados", "Estado", estado_profesor_nombre)
        aula_id = obtener_id_por_nombre("Aulas", "NombreAula", aula_nombre)

        # Validar que todos los IDs existan
        if not all([rol_id, estado_usuario_id, estado_id, aula_id]):
            messages.error(request, "Uno o más valores escritos no existen en la base de datos.")
            request.session['open_form'] = 'agregarProfesorForm'
            return redirect('my_proyecto:administrador')

        hashed_password = make_password(password)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL CrearUsuarioYProfesor(
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                """, [
                    username, hashed_password, rol_id, estado_usuario_id,
                    nombre, ap_pat, ap_mat, num_empleado, direccion,
                    email, telefono, fecha_ingreso if fecha_ingreso else None,
                    estado_id, especialidad, aula_id
                ])

            messages.success(request, "Profesor y usuario registrados correctamente.")
            request.session.pop('open_form', None)
            return redirect('my_proyecto:administrador')

        except IntegrityError:
            logger.exception("Error de integridad al crear usuario/profesor")
            messages.error(request, "Usuario o correo ya existen.")
            request.session['open_form'] = 'agregarProfesorForm'
            return redirect('my_proyecto:administrador')

        except OperationalError:
            logger.exception("Error de conexión a la base de datos")
            messages.error(request, "No se pudo conectar a la base de datos.")
            request.session['open_form'] = 'agregarProfesorForm'
            return redirect('my_proyecto:administrador')

        except Exception as e:
            logger.exception("Error inesperado")
            messages.error(request, f"Error inesperado: {e}")
            request.session['open_form'] = 'agregarProfesorForm'
            return redirect('my_proyecto:administrador')

    # Si es GET, cargar selects (puedes mantenerlos si usas autocompletado o validación)
    with connection.cursor() as cursor:
        cursor.execute("SELECT Id, Nombre FROM RolesPermisos")
        roles = cursor.fetchall()
        cursor.execute("SELECT Id, EstadoUs FROM EstadoUsuario")
        estados_usuario = cursor.fetchall()
        cursor.execute("SELECT Id, Estado FROM Estados")
        estados_profesor = cursor.fetchall()
        cursor.execute("SELECT Id, NombreAula FROM Aulas")
        aulas = cursor.fetchall()

    return render(request, 'my_proyecto/administrador.html', {
        'roles': roles,
        'estados_usuario': estados_usuario,
        'estados_profesor': estados_profesor,
        'aulas': aulas,
        'username': request.session.get('username')
    })

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

