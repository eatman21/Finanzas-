from rest_framework import serializers
from .models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito, Recomendacion


class PerfilFinancieroSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilFinanciero
        fields = [
            'id', 'usuario', 'ingreso_mensual', 'otros_ingresos',
            'gastos_fijos', 'ahorro_mensual', 'ahorro_actual',
            'score_crediticio', 'fecha_actualizacion',
            'ingreso_total', 'capacidad_ahorro', 'capacidad_endeudamiento'
        ]
        read_only_fields = ['usuario', 'fecha_actualizacion',
                            'ingreso_total', 'capacidad_ahorro', 'capacidad_endeudamiento']


class DeudaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deuda
        fields = [
            'id', 'perfil', 'tipo', 'nombre', 'saldo_actual',
            'pago_mensual', 'tasa_interes', 'fecha_inicio', 'plazo_meses'
        ]
        read_only_fields = ['perfil']


class ObjetivoFinancieroSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoFinanciero
        fields = [
            'id', 'perfil', 'tipo', 'nombre', 'monto_objetivo',
            'plazo_meses', 'fecha_creacion', 'activo',
            'ahorro_mensual_requerido'
        ]
        read_only_fields = ['perfil', 'fecha_creacion',
                            'ahorro_mensual_requerido']


class SimulacionCreditoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulacionCredito
        fields = [
            'id', 'perfil', 'tipo', 'nombre', 'valor_propiedad',
            'enganche_porcentaje', 'tasa_interes_anual', 'plazo_anos',
            'gastos_adicionales', 'fecha_simulacion',
            'monto_enganche', 'monto_credito', 'plazo_meses',
            'tasa_mensual', 'pago_mensual', 'pago_total',
            'intereses_totales'
        ]
        read_only_fields = [
            'perfil', 'fecha_simulacion', 'monto_enganche',
            'monto_credito', 'plazo_meses', 'tasa_mensual',
            'pago_mensual', 'pago_total', 'intereses_totales'
        ]


class RecomendacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recomendacion
        fields = [
            'id', 'perfil', 'titulo', 'descripcion',
            'prioridad', 'fecha_creacion', 'activa'
        ]
        read_only_fields = ['perfil', 'fecha_creacion']


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard summary data"""
    perfil = PerfilFinancieroSerializer()
    deudas = DeudaSerializer(many=True)
    objetivos = ObjetivoFinancieroSerializer(many=True)
    simulaciones = SimulacionCreditoSerializer(many=True)
    recomendaciones = RecomendacionSerializer(many=True)

    total_deudas = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_objetivos = serializers.DecimalField(max_digits=12, decimal_places=2)
    capacidad_endeudamiento_utilizada = serializers.DecimalField(
        max_digits=5, decimal_places=2)
