# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Administrador(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    usuarioid = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='UsuarioId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'administrador'


class Emailservicios(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    destino = models.CharField(db_column='Destino', max_length=100, blank=True, null=True)  # Field name made lowercase.
    mensaje = models.TextField(db_column='Mensaje', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'emailservicios'


class Generadorreportes(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    contenido = models.TextField(db_column='Contenido', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'generadorreportes'


class Grupo(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)  # Field name made lowercase.
    profesorid = models.ForeignKey('Profesor', models.DO_NOTHING, db_column='ProfesorId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'grupo'


class Horario(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dia = models.CharField(db_column='Dia', max_length=15, blank=True, null=True)  # Field name made lowercase.
    horarioinicio = models.TimeField(db_column='HorarioInicio', blank=True, null=True)  # Field name made lowercase.
    horafin = models.TimeField(db_column='HoraFin', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'horario'


class Login(models.Model):
    usuarioid = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='UsuarioId', primary_key=True)
    usuario = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=100)

    class Meta:
        db_table = 'Login'  # nombre exacto de tu tabla en MySQL


    def __str__(self):
        return self.usuario


class Materia(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='Codigo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    profesorid = models.ForeignKey('Profesor', models.DO_NOTHING, db_column='ProfesorId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'materia'


class Materiagrupo(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    materiaid = models.ForeignKey(Materia, models.DO_NOTHING, db_column='MateriaId', blank=True, null=True)  # Field name made lowercase.
    grupoid = models.ForeignKey(Grupo, models.DO_NOTHING, db_column='GrupoId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'materiagrupo'


class Materiahorario(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    materiaid = models.ForeignKey(Materia, models.DO_NOTHING, db_column='MateriaId', blank=True, null=True)  # Field name made lowercase.
    horarioid = models.ForeignKey(Horario, models.DO_NOTHING, db_column='HorarioId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'materiahorario'


class Preferenciamateria(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    profesorid = models.ForeignKey('Profesor', models.DO_NOTHING, db_column='ProfesorId', blank=True, null=True)  # Field name made lowercase.
    materiaid = models.ForeignKey(Materia, models.DO_NOTHING, db_column='MateriaId', blank=True, null=True)  # Field name made lowercase.
    preferencianivel = models.IntegerField(db_column='PreferenciaNivel', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'preferenciamateria'


class Profesor(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)  # Field name made lowercase.
    especialidad = models.CharField(db_column='Especialidad', max_length=100, blank=True, null=True)  # Field name made lowercase.
    usuarioid = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='UsuarioId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'profesor'


class Pushservicios(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    usuarioid = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='UsuarioId', blank=True, null=True)  # Field name made lowercase.
    mensaje = models.TextField(db_column='Mensaje', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pushservicios'


class Registroeventos(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    generadorreporteid = models.ForeignKey(Generadorreportes, models.DO_NOTHING, db_column='GeneradorReporteId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'registroeventos'


class Registrovisitas(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    usuario = models.CharField(db_column='Usuario', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fechaentrada = models.DateTimeField(db_column='FechaEntrada', blank=True, null=True)  # Field name made lowercase.
    fechasalida = models.DateTimeField(db_column='FechaSalida', blank=True, null=True)  # Field name made lowercase.
    generadorreporteid = models.ForeignKey(Generadorreportes, models.DO_NOTHING, db_column='GeneradorReporteId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'registrovisitas'


class Rolespermisos(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rolespermisos'


class Usuario(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=100, blank=True, null=True)  # Field name made lowercase.
    rol = models.CharField(db_column='Rol', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario'
