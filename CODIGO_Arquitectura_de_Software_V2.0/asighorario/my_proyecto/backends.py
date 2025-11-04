from .models import Login, Usuario

class CustomAuthBackend:
    """
    Un backend de autenticación personalizado para usar las tablas
    'Login' y 'Usuario'.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            # 1. Buscar el usuario en la tabla Login
            login_info = Login.objects.get(usuario=username)

            # 2. Verificar la contraseña (¡ADVERTENCIA DE SEGURIDAD ABAJO!)
            if login_info.contrasena == password:
                # 3. Si es correcta, obtener el objeto Usuario completo
                user = Usuario.objects.get(id=login_info.usuario_id_id)
                return user # Devolver el objeto Usuario si el login es exitoso
            return None
        except Login.DoesNotExist:
            # El usuario no existe en la tabla Login
            return None

    def get_user(self, user_id):
        try:
            # Django usa esto para obtener el objeto usuario en cada petición
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None