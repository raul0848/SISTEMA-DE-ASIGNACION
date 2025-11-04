"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from my_proyecto import views as login_views  # Importa las vistas de login_app y les da un alias
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logins/', include('my_proyecto.urls')),  # Todas las URLs de my_proyecto se manejan aquí
    path('', include('my_proyecto.urls')),   # correcto: incluye las urls de la app
    path('', RedirectView.as_view(url='/my_proyecto/', permanent=False), name='index'),  # Redirige la raíz
    
]
