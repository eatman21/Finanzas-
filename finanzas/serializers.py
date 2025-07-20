from .legacy_models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito, Recomendacion
from .models.account import Account
from .models.transaction import Transaction, Category
from .models.budget import Budget
from rest_framework import serializers


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


# New Model Serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'icon', 'color', 'parent',
            'is_income', 'is_expense', 'created_at'
        ]


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'user', 'name', 'account_type', 'currency',
            'initial_balance', 'current_balance', 'description',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'current_balance',
                            'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'account', 'account_name', 'transaction_type',
            'category', 'category_name', 'amount', 'description', 'notes',
            'date', 'is_recurring', 'is_cancelled', 'destination_account',
            'receipt', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    spent_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True)
    spent_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'name', 'period', 'start_date', 'end_date',
            'total_amount', 'description', 'is_active', 'created_at',
            'updated_at', 'spent_amount', 'remaining_amount', 'spent_percentage'
        ]
        read_only_fields = ['user', 'spent_amount', 'remaining_amount',
                            'spent_percentage', 'created_at', 'updated_at']


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
