from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),  # Página principal de login_app
    path('login/', views.login_view, name='login'),
    path('inicio_admin/', views.inicio_admin, name='inicio_admin'),
    path('inicio_profesor/', views.inicio_profesor, name='inicio_profesor'),
    path('gestionar_profesores/', views.gestionar_profesores, name='gestionar_profesores'),
    path('profesores/agregar/', views.agregar_profesor, name='agregar_profesor'),
    path('profesores/buscar/', views.buscar_profesor, name='buscar_profesor'),
    path('profesores/editar/<int:profesor_id>/', views.editar_profesor, name='editar_profesor'),
    path('profesores/eliminar/<int:profesor_id>/', views.eliminar_profesor, name='eliminar_profesor'),
    path('asignar_profesor_materia/', views.asignar_profesor_materia, name='asignar_profesor_materia'),
    path('', views.login_list, name='login_list'),
    path('registro/', views.signup, name='signup'),
    path('registro_admin/', views.signup_admin, name='signup_admin'),
    path('create/', views.login_create, name='login_create'),
    path('update/<int:pk>/', views.login_update, name='login_update'),
    path('delete/<int:pk>/', views.login_delete, name='login_delete'),
    path('obtener_datos/<int:pk>/', views.obtener_datos, name='obtener_datos'),
    path('logout/', views.logout_view, name='logout'),

]
