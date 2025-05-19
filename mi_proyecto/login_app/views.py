from django.shortcuts import render, redirect, get_object_or_404
from .models import Login
from .forms import LoginForm
from django.http import HttpResponse
from django.db import connection
from django.contrib import messages


def home(request):
    return render(request, 'login_app/home.html')

def login_list(request):
    return HttpResponse("Login List Page")

## def index(request):
   ##  return HttpResponse("Hola desde login_app")
def signup(request):
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
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login_app/signup.html', {'form': form})

def signup_admin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario_nombre = form.cleaned_data['usuario']
            usuario_email = f'{usuario_nombre}@admin.com'
            rol = 'Administrador'

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Usuario (Nombre, Email, Rol)
                    VALUES (%s, %s, %s)
                """, [usuario_nombre, usuario_email, rol])
                cursor.execute("SELECT LAST_INSERT_ID()")
                usuario_id = cursor.fetchone()[0]

                login = form.save(commit=False)
                login.usuarioid_id = usuario_id
                login.save()

                # Crear en tabla Administrador
                cursor.execute("""
                    INSERT INTO Administrador (UsuarioId) VALUES (%s)
                """, [usuario_id])

            messages.success(request, "Registro exitoso como administrador")
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login_app/signup.html', {'form': form})



# CREATE
def login_create(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login_list')
    return render(request, 'login_app/login_form.html', {'form': form})

# READ
def login_list(request):
    logins = Login.objects.all()
    return render(request, 'login_app/login_list.html', {'logins': logins})

# UPDATE
def login_update(request, pk):
    login = get_object_or_404(Login, pk=pk)
    form = LoginForm(request.POST or None, instance=login)
    if form.is_valid():
        form.save()
        return redirect('login_list')
    return render(request, 'login_app/login_form.html', {'form': form})

# DELETE
def login_delete(request, pk):
    login = get_object_or_404(Login, pk=pk)
    if request.method == "POST":
        login.delete()
        return redirect('login_list')
    return render(request, 'login_app/login_confirm_delete.html', {'login': login})

def obtener_datos(request, pk):
    login = get_object_or_404(Login, pk=pk)
    return render(request, 'login_app/login_detail.html', {'login': login})

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.Id, u.Nombre, u.Rol
                FROM Login l
                JOIN Usuario u ON l.UsuarioId = u.Id
                WHERE l.Usuario = %s AND l.Contrasena = %s
            """, [usuario, contrasena])
            resultado = cursor.fetchone()

        if resultado:
            usuario_id, nombre, rol = resultado
            # Guardamos los datos en sesión
            request.session['usuario_id'] = usuario_id
            request.session['usuario_nombre'] = nombre
            request.session['rol'] = rol

            if rol == 'Administrador':
                return redirect('inicio_admin')
            elif rol == 'Profesor':
                return redirect('inicio_profesor')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'login_app/login.html')


# PASO 2: Vista de administrador con botón y enlace a CRUD

def inicio_admin(request):
    return render(request, 'login_app/inicio_admin.html')


# PASO 3: Vista de profesor y consulta de su información

def inicio_profesor(request):
    usuario_id = request.session.get('usuario_id')
    datos_profesor = {}

    with connection.cursor() as cursor:
        # Buscar datos del profesor
        cursor.execute("SELECT Id, Nombre, Especialidad FROM Profesor WHERE UsuarioId = %s", [usuario_id])
        prof_row = cursor.fetchone()
        if prof_row:
            prof_id, nombre, especialidad = prof_row
            datos_profesor['nombre'] = nombre
            datos_profesor['especialidad'] = especialidad

            # Buscar materias
            cursor.execute("SELECT Id, Nombre FROM Materia WHERE ProfesorId = %s", [prof_id])
            datos_profesor['materias'] = cursor.fetchall()

            # Buscar horarios
            cursor.execute("""
                SELECT h.Dia, h.HorarioInicio, h.HoraFin
                FROM Horario h
                JOIN MateriaHorario mh ON mh.HorarioId = h.Id
                JOIN Materia m ON mh.MateriaId = m.Id
                WHERE m.ProfesorId = %s
            """, [prof_id])
            datos_profesor['horarios'] = cursor.fetchall()

    return render(request, 'login_app/inicio_profesor.html', {'profesor': datos_profesor})


# CRUD DE PROFESORES CON ASIGNACIÓN DE MATERIAS USANDO GALE-SHAPLEY

def gestionar_profesores(request):
    profesores = []
    materias = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT Id, Nombre FROM Profesor")
        profesores = cursor.fetchall()
        cursor.execute("SELECT Id, Nombre FROM Materia")
        materias = cursor.fetchall()

    return render(request, 'login_app/gestionar_profesores.html', {
        'profesores': profesores,
        'materias': materias
    })

def gestionar_profesores(request):
    return render(request, 'login_app/gestionar_profesores.html')


def asignar_profesor_materia(request):
    if request.method == 'POST':
        id_profesor = int(request.POST.get('id_profesor'))
        id_materia = int(request.POST.get('id_materia'))

        with connection.cursor() as cursor:
            # Validar existencia de profesor y materia
            cursor.execute("SELECT COUNT(*) FROM Profesor WHERE Id = %s", [id_profesor])
            if cursor.fetchone()[0] == 0:
                messages.error(request, "Profesor no encontrado.")
                return redirect('gestionar_profesores')

            cursor.execute("SELECT COUNT(*) FROM Materia WHERE Id = %s", [id_materia])
            if cursor.fetchone()[0] == 0:
                messages.error(request, "Materia no encontrada.")
                return redirect('gestionar_profesores')

            # Verificar que la materia no tenga ya asignado profesor
            cursor.execute("SELECT ProfesorId FROM Materia WHERE Id = %s", [id_materia])
            current = cursor.fetchone()[0]
            if current == id_profesor:
                messages.info(request, "Esta materia ya está asignada a este profesor.")
            elif current is None:
                cursor.execute("UPDATE Materia SET ProfesorId = %s WHERE Id = %s", [id_profesor, id_materia])
                messages.success(request, f"Materia ID {id_materia} asignada al Profesor ID {id_profesor}")
            else:
                messages.warning(request, f"La materia ya está asignada a otro profesor (ID {current})")

    return redirect('gestionar_profesores')

def logout_view(request):
    request.session.flush()  # Elimina todos los datos de sesión
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('home')  # Redirige a la página principal

def agregar_profesor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        especialidad = request.POST.get('especialidad')
        usuario_id = request.POST.get('usuario_id')

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Profesor (Nombre, Especialidad, UsuarioId) VALUES (%s, %s, %s)", [nombre, especialidad, usuario_id])
            messages.success(request, "Profesor agregado correctamente.")
        return redirect('gestionar_profesores')
    return render(request, 'login_app/agregar_profesor.html')

def buscar_profesor(request):
    profesor = None
    if request.method == 'POST':
        profesor_id = request.POST.get('id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT Id, Nombre, Especialidad FROM Profesor WHERE Id = %s", [profesor_id])
            profesor = cursor.fetchone()
    return render(request, 'login_app/buscar_profesor.html', {'profesor': profesor})

def editar_profesor(request, profesor_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        especialidad = request.POST.get('especialidad')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Profesor SET Nombre=%s, Especialidad=%s WHERE Id=%s", [nombre, especialidad, profesor_id])
            messages.success(request, "Profesor actualizado.")
        return redirect('gestionar_profesores')
    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Nombre, Especialidad FROM Profesor WHERE Id=%s", [profesor_id])
            profesor = cursor.fetchone()
        return render(request, 'login_app/editar_profesor.html', {'profesor': profesor, 'id': profesor_id})

def eliminar_profesor(request, profesor_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Profesor WHERE Id=%s", [profesor_id])
            messages.success(request, "Profesor eliminado.")
        return redirect('gestionar_profesores')
    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Nombre FROM Profesor WHERE Id=%s", [profesor_id])
            profesor = cursor.fetchone()
        return render(request, 'login_app/eliminar_profesor.html', {'profesor': profesor, 'id': profesor_id})

def gestionar_profesores(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT Id, Nombre, Especialidad FROM Profesor")
        profesores = cursor.fetchall()
    return render(request, 'login_app/gestionar_profesores.html', {
        'profesores': profesores
    })