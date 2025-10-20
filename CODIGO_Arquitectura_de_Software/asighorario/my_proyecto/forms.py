from django import forms
from .models import Login
from .models import Materia
from .models import Materia
from .models import Profesor, Usuario
from django.core.exceptions import ValidationError

# my_proyecto/forms.py
class ProfesorForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    ap_pat = forms.CharField(max_length=100, required=False)
    ap_mat = forms.CharField(max_length=100, required=False)
    especialidad = forms.CharField(max_length=100, required=False)
    num_empleado = forms.CharField(max_length=100, required=False)
    direccion = forms.CharField(max_length=250, required=False)
    email = forms.EmailField()
    telefono = forms.CharField(max_length=30, required=False)
    fecha_ingreso = forms.DateField(required=False)
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    #estas 3 no 
    model = Usuario
    fields = ['nombre', 'email', 'rol']
    especialidad = forms.CharField(required=False, label="Especialidad")

    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El username ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Profesor.objects.filter(email=email).exists():
            raise ValidationError("El email ya está registrado para otro profesor.")
        return email


class LoginForm(forms.ModelForm):
    ROL_CHOICES = [
        ('Profesor', 'Profesor'),
        ('Administrador', 'Administrador'),
    ]

    rol = forms.ChoiceField(choices=ROL_CHOICES, label="Tipo de Usuario")
    especialidad = forms.CharField(max_length=100, required=False, label="Especialidad (solo si es profesor)")

    class Meta:
        model = Login
        fields = ['usuario', 'contrasena']
        labels = {
            'usuario': 'Nombre de usuario',
            'contrasena': 'Contraseña',
        }
        widgets = {
            'contrasena': forms.PasswordInput(),
        }

    # Validación adicional
    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        especialidad = cleaned_data.get('especialidad')

        if rol == 'Profesor' and not especialidad:
            self.add_error('especialidad', 'Este campo es obligatorio para profesores.')


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['nombre', 'codigo', 'horario_inicio', 'horario_fin', 'preferencia']
        labels = {
            'nombre': 'Nombre de la materia',
            'codigo': 'Código de materia',
            'profesor': 'Profesor',
            'horario_inicio': 'Horario de inicio',
            'horario_fin': 'Horario de fin',
            'preferencia': 'Nivel de preferencia',
        }
        widgets = {
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fin': forms.TimeInput(attrs={'type': 'time'}),
            'preferencia': forms.Select(choices=[
                ('bajo', 'Bajo'),
                ('medio', 'Medio'),
                ('alto', 'Alto')
            ])
        }
