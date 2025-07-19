from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'perfiles', api_views.PerfilFinancieroViewSet,
                basename='perfil')
router.register(r'deudas', api_views.DeudaViewSet, basename='deuda')
router.register(
    r'objetivos', api_views.ObjetivoFinancieroViewSet, basename='objetivo')
router.register(r'simulaciones',
                api_views.SimulacionCreditoViewSet, basename='simulacion')
router.register(r'recomendaciones',
                api_views.RecomendacionViewSet, basename='recomendacion')

app_name = 'finanzas_api'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]
