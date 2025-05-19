from django.contrib import admin
from django.urls import path, include
from login_app import views as login_views  # Importa las vistas de login_app y les da un alias
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logins/', include('login_app.urls')),  # Todas las URLs de login_app se manejan aquí
    path('', RedirectView.as_view(url='/logins/', permanent=False), name='home'),  # Redirige la raíz
]
