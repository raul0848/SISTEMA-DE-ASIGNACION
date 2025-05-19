from django import forms
from .models import Login


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

