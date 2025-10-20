from django.db import models

# my_proyecto/models.py
class EstadoUsuario(models.Model):
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.estado

class RolesPermisos(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# Modelo que representa tu tabla 'Usuario'
class Usuario(models.Model):
    # Omitimos el Id porque Django lo maneja, pero lo vinculamos al campo real
    id = models.AutoField(primary_key=True, db_column='Id')
    nombre = models.CharField(max_length=100, db_column='Nombre')
    email = models.CharField(max_length=100, unique=True, db_column='Email')
    rol = models.CharField(max_length=50, db_column='Rol')
    fecha_alta = models.DateField(null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)  # hash aquí
    rol = models.ForeignKey(RolesPermisos, null=True, blank=True, on_delete=models.RESTRICT)
    estado = models.ForeignKey(EstadoUsuario, null=True, blank=True, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'Usuario'
        # Si la tabla ya existe en la BD y no quieres que Django la maneje:
        managed = False

    def __str__(self):
        return self.nombre

# Modelo que representa tu tabla 'Login'
class Login(models.Model):
    usuario_fk = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, db_column='UsuarioId')
    usuario = models.CharField(max_length=100, unique=True, db_column='Usuario')
    contrasena = models.CharField(max_length=100, db_column='Contrasena')

    class Meta:
        db_table = 'Login'
        managed = False


class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='UsuarioId', unique=True)

    class Meta:
        db_table = 'Administrador'
        managed = False


class Profesor(models.Model):
    nombre = models.CharField(max_length=100, db_column='Nombre')
    especialidad = models.CharField(max_length=100, db_column='Especialidad')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column='UsuarioId')
    usuario = models.OneToOneField(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='profesor')
    materias = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=50, default='Profesor')
    ap_pat = models.CharField(max_length=100, blank=True, null=True)
    ap_mat = models.CharField(max_length=100, blank=True, null=True)
    num_empleado = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    especialidad = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'Profesor'
        managed = False

    def __str__(self):
        return f"{self.nombre} {self.ap_pat or ''} {self.ap_mat or ''}"

class Materia(models.Model):
    nombre = models.CharField(max_length=100, db_column='Nombre')
    codigo = models.CharField(max_length=20, db_column='Codigo')
    profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, db_column='ProfesorId')
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    preferencia = models.CharField(max_length=20, choices=[
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto')
    ])

    class Meta:
        db_table = 'Materia'
        managed = False

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Horario(models.Model):
    dia = models.CharField(max_length=15, db_column='Dia')
    horario_inicio = models.TimeField(db_column='HorarioInicio')
    hora_fin = models.TimeField(db_column='HoraFin')

    class Meta:
        db_table = 'Horario'
        managed = False

class MateriaHorario(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, db_column='MateriaId')
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, db_column='HorarioId')

    class Meta:
        db_table = 'MateriaHorario'
        managed = False

class Grupo(models.Model):
    nombre = models.CharField(max_length=100, db_column='Nombre')
    profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, db_column='ProfesorId')

    class Meta:
        db_table = 'Grupo'
        managed = False

class MateriaGrupo(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, db_column='MateriaId')
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, db_column='GrupoId')

    class Meta:
        db_table = 'MateriaGrupo'
        managed = False

class PreferenciaMateria(models.Model):
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, db_column='ProfesorId')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, db_column='MateriaId')
    preferencia_nivel = models.IntegerField(db_column='PreferenciaNivel')

    class Meta:
        db_table = 'PreferenciaMateria'
        managed = False
