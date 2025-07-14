from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'finanzas'


def home(request):
    """Redirect home to dashboard"""
    return redirect('finanzas:dashboard')


urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil_financiero, name='perfil_financiero'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('deudas/', views.lista_deudas, name='lista_deudas'),
    path('deudas/nueva/', views.nueva_deuda, name='nueva_deuda'),
    path('deudas/<int:pk>/editar/', views.editar_deuda, name='editar_deuda'),
    path('deudas/<int:pk>/eliminar/', views.eliminar_deuda, name='eliminar_deuda'),
    path('objetivos/', views.lista_objetivos, name='lista_objetivos'),
    path('objetivos/nuevo/', views.nuevo_objetivo, name='nuevo_objetivo'),
    path('objetivos/<int:pk>/editar/',
         views.editar_objetivo, name='editar_objetivo'),
    path('objetivos/<int:pk>/eliminar/',
         views.eliminar_objetivo, name='eliminar_objetivo'),
    path('simulaciones/', views.lista_simulaciones, name='lista_simulaciones'),
    path('simulaciones/nueva/', views.nueva_simulacion, name='nueva_simulacion'),
    path('simulaciones/<int:pk>/', views.detalle_simulacion,
         name='detalle_simulacion'),
    path('simulaciones/<int:pk>/eliminar/',
         views.eliminar_simulacion, name='eliminar_simulacion'),
    path('recomendaciones/', views.lista_recomendaciones,
         name='lista_recomendaciones'),
]
