from django.contrib import admin
from .legacy_models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito, Recomendacion
from .models.account import Account, AccountType, Currency
from .models.transaction import Transaction, Category
from .models.budget import Budget, BudgetCategory, BudgetPeriod
from .models.report import Report, ReportType


@admin.register(PerfilFinanciero)
class PerfilFinancieroAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'ingreso_total', 'capacidad_ahorro',
                    'capacidad_endeudamiento', 'score_crediticio', 'fecha_actualizacion']
    list_filter = ['score_crediticio', 'fecha_actualizacion']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['ingreso_total', 'capacidad_ahorro',
                       'capacidad_endeudamiento', 'fecha_actualizacion']

    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario',)
        }),
        ('Ingresos', {
            'fields': ('ingreso_mensual', 'otros_ingresos', 'ingreso_total')
        }),
        ('Gastos y Ahorro', {
            'fields': ('gastos_fijos', 'ahorro_mensual', 'ahorro_actual', 'capacidad_ahorro')
        }),
        ('Capacidad de Endeudamiento', {
            'fields': ('capacidad_endeudamiento',)
        }),
        ('Información Crediticia', {
            'fields': ('score_crediticio',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'perfil', 'tipo', 'saldo_actual',
                    'pago_mensual', 'tasa_interes', 'fecha_inicio']
    list_filter = ['tipo', 'fecha_inicio']
    search_fields = ['nombre', 'perfil__usuario__username']
    date_hierarchy = 'fecha_inicio'


@admin.register(ObjetivoFinanciero)
class ObjetivoFinancieroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'perfil', 'tipo', 'monto_objetivo',
                    'plazo_meses', 'ahorro_mensual_requerido', 'activo', 'fecha_creacion']
    list_filter = ['tipo', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'perfil__usuario__username']
    readonly_fields = ['ahorro_mensual_requerido', 'fecha_creacion']
    date_hierarchy = 'fecha_creacion'


@admin.register(SimulacionCredito)
class SimulacionCreditoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'perfil', 'tipo', 'valor_propiedad', 'monto_enganche',
                    'monto_credito', 'pago_mensual', 'es_viable', 'fecha_simulacion']
    list_filter = ['tipo', 'fecha_simulacion']
    search_fields = ['nombre', 'perfil__usuario__username']
    readonly_fields = ['monto_enganche', 'monto_credito', 'plazo_meses', 'tasa_mensual',
                       'pago_mensual', 'pago_total', 'intereses_totales', 'es_viable', 'fecha_simulacion']
    date_hierarchy = 'fecha_simulacion'

    fieldsets = (
        ('Información Básica', {
            'fields': ('perfil', 'tipo', 'nombre')
        }),
        ('Detalles del Crédito', {
            'fields': ('valor_propiedad', 'enganche_porcentaje', 'monto_enganche', 'monto_credito')
        }),
        ('Términos del Crédito', {
            'fields': ('tasa_interes_anual', 'plazo_anos', 'plazo_meses', 'tasa_mensual')
        }),
        ('Cálculos', {
            'fields': ('pago_mensual', 'pago_total', 'intereses_totales', 'es_viable')
        }),
        ('Gastos Adicionales', {
            'fields': ('gastos_adicionales',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_simulacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'perfil',
                    'prioridad', 'activa', 'fecha_creacion']
    list_filter = ['prioridad', 'activa', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion', 'perfil__usuario__username']
    date_hierarchy = 'fecha_creacion'


# New Models Admin
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type',
                    'currency', 'current_balance', 'is_active']
    list_filter = ['account_type', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'user__username', 'description']
    readonly_fields = ['current_balance', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_income', 'is_expense', 'color']
    list_filter = ['is_income', 'is_expense', 'parent']
    search_fields = ['name']
    list_editable = ['color']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'user', 'account',
                    'transaction_type', 'amount', 'date', 'is_cancelled']
    list_filter = ['transaction_type', 'date',
                   'is_cancelled', 'is_recurring', 'category']
    search_fields = ['description', 'user__username', 'account__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    list_per_page = 50


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'period', 'total_amount',
                    'spent_amount', 'remaining_amount', 'is_active']
    list_filter = ['period', 'is_active', 'start_date']
    search_fields = ['name', 'user__username']
    readonly_fields = ['spent_amount', 'remaining_amount',
                       'spent_percentage', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ['budget', 'category', 'allocated_amount',
                    'spent_amount', 'remaining_amount']
    list_filter = ['budget', 'category']
    search_fields = ['budget__name', 'category__name']
    readonly_fields = ['spent_amount', 'remaining_amount', 'spent_percentage']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'report_type',
                    'start_date', 'end_date', 'is_saved']
    list_filter = ['report_type', 'is_saved', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
