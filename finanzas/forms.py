from django import forms
from .legacy_models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito
from .models.account import Account
from .models.transaction import Transaction, Category
from .models.budget import Budget, BudgetCategory
from django.core.validators import MinValueValidator
from decimal import Decimal


class PerfilFinancieroForm(forms.ModelForm):
    class Meta:
        model = PerfilFinanciero
        fields = [
            'ingreso_mensual', 'otros_ingresos', 'gastos_fijos',
            'ahorro_mensual', 'ahorro_actual', 'score_crediticio'
        ]
        widgets = {
            'ingreso_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
            'otros_ingresos': forms.NumberInput(attrs={'class': 'form-control'}),
            'gastos_fijos': forms.NumberInput(attrs={'class': 'form-control'}),
            'ahorro_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
            'ahorro_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'score_crediticio': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DeudaForm(forms.ModelForm):
    class Meta:
        model = Deuda
        fields = [
            'tipo', 'nombre', 'saldo_actual', 'pago_mensual',
            'tasa_interes', 'fecha_inicio', 'plazo_meses'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'saldo_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'pago_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
            'tasa_interes': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plazo_meses': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ObjetivoFinancieroForm(forms.ModelForm):
    class Meta:
        model = ObjetivoFinanciero
        fields = [
            'tipo', 'nombre', 'monto_objetivo', 'plazo_meses', 'activo'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_objetivo': forms.NumberInput(attrs={'class': 'form-control'}),
            'plazo_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SimulacionCreditoForm(forms.ModelForm):
    class Meta:
        model = SimulacionCredito
        fields = [
            'tipo', 'nombre', 'valor_propiedad', 'enganche_porcentaje',
            'tasa_interes_anual', 'plazo_anos', 'gastos_adicionales'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_propiedad': forms.NumberInput(attrs={'class': 'form-control'}),
            'enganche_porcentaje': forms.NumberInput(attrs={'class': 'form-control'}),
            'tasa_interes_anual': forms.NumberInput(attrs={'class': 'form-control'}),
            'plazo_anos': forms.NumberInput(attrs={'class': 'form-control'}),
            'gastos_adicionales': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# New Financial Models Forms
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'name', 'account_type', 'currency', 'initial_balance',
            'description', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'initial_balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'account', 'transaction_type', 'category', 'amount',
            'description', 'date', 'notes', 'is_recurring'
        ]
        widgets = {
            'account': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['account'].queryset = Account.objects.filter(
                user=user, is_active=True)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name', 'icon', 'color', 'parent', 'is_income', 'is_expense'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'is_income': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_expense': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'name', 'period', 'start_date', 'end_date',
            'total_amount', 'description', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ['category', 'allocated_amount', 'notes']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'allocated_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
