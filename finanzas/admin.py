from django.contrib import admin
from .models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito, Recomendacion


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
