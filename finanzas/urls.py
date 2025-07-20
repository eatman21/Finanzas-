from django.urls import path
from django.shortcuts import redirect
from finanzas import views

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
    path('calculadora/', views.calculadora_moderna, name='calculadora'),

    # API endpoints
    path('api/dashboard-summary/', views.api_dashboard_summary,
         name='api_dashboard_summary'),

    # New Financial Models URLs
    # Accounts
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/nueva/', views.account_create, name='account_create'),
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'),
    path('accounts/<int:pk>/editar/', views.account_update, name='account_update'),
    path('accounts/<int:pk>/eliminar/',
         views.account_delete, name='account_delete'),

    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/nueva/', views.transaction_create,
         name='transaction_create'),
    path('transactions/<int:pk>/', views.transaction_detail,
         name='transaction_detail'),
    path('transactions/<int:pk>/editar/',
         views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/eliminar/',
         views.transaction_delete, name='transaction_delete'),

    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/<int:pk>/', views.budget_detail, name='budget_detail'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
]
