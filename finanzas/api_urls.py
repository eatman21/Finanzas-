from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()

# Legacy API endpoints
router.register(r'perfiles', api_views.PerfilFinancieroViewSet,
                basename='perfil')
router.register(r'deudas', api_views.DeudaViewSet, basename='deuda')
router.register(
    r'objetivos', api_views.ObjetivoFinancieroViewSet, basename='objetivo')
router.register(r'simulaciones',
                api_views.SimulacionCreditoViewSet, basename='simulacion')
router.register(r'recomendaciones',
                api_views.RecomendacionViewSet, basename='recomendacion')

# Modern API endpoints
router.register(r'accounts', api_views.AccountViewSet, basename='account')
router.register(r'transactions', api_views.TransactionViewSet,
                basename='transaction')
router.register(r'categories', api_views.CategoryViewSet, basename='category')
router.register(r'budgets', api_views.BudgetViewSet, basename='budget')

app_name = 'finanzas_api'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]

# Add these imports at the top if debug mode for API documentation
try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView
    )
    from django.conf import settings

    # API Documentation endpoints (only in DEBUG mode or if explicitly enabled)
    if getattr(settings, 'DEBUG', False):
        urlpatterns += [
            path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
            path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
                 name='swagger-ui'),
            path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'),
                 name='redoc'),
        ]
except ImportError:
    pass  # drf-spectacular not installed
