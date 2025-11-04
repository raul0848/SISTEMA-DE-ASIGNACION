from django.urls import path
from . import views

app_name = 'my_proyecto'

urlpatterns = [
    path('', views.index, name='index'),
    path('administrador/', views.administrador, name='administrador'),
    path('maestros/', views.maestros, name='maestros'),
    path('menu/', views.menu_profesor, name='menu_profesores'),

    path('signup/', views.signup, name='signup'),
    path('login_api/', views.login_api, name='login_api'),
    path('api/login_profesor/', views.login_api_profesor, name='login_api_profesor'),
    path('login/profesor/', views.login_api_profesor, name='login_api_profesor_alias'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.index, name='login'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),

    path('admin/', views.vista_administrador, name='administrador'),

    path('agregar_profesor/', views.agregar_profesor, name='agregar_profesor'),
    path('admin/poblar_catalogos/', views.poblar_catalogos),
    path('admin/', views.administrador_view, name='administrador'),
    path('admin/agregar_profesor/', views.agregar_profesor, name='agregar_profesor'),
    path('limpiar_open_form/', views.limpiar_open_form, name='limpiar_open_form'),

    path('buscar_profesor/', views.buscar_profesor, name='buscar_profesor'),
    path('editar_profesor/<int:id>/', views.editar_profesor, name='editar_profesor'),
    path('eliminar_profesor/<int:id>/', views.eliminar_profesor, name='eliminar_profesor'),

    path('agregar_materia/', views.agregar_materia, name='agregar_materia'),
    path('agregar_horario/', views.agregar_horario, name='agregar_horario'),
    path('gestionar_profesores/', views.gestionar_profesores, name='gestionar_profesores'),

    path('profesor/<int:profesor_id>/horario/', views.horario_profesor, name='horario_profesor'),
    path('profesor/menu/', views.menu_profesor, name='menu_profesor'),

    path('administrador/agregar_profesor/', views.agregar_profesor, name='agregar_profesor'),
    path('administrador/', views.administrador_view, name='administrador'),

]
