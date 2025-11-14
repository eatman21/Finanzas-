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
            'ingreso_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            }),
            'otros_ingresos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'gastos_fijos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'ahorro_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'ahorro_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'score_crediticio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '300',
                'max': '850'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        ingreso = cleaned_data.get('ingreso_mensual', Decimal('0'))
        otros_ingresos = cleaned_data.get('otros_ingresos', Decimal('0'))
        gastos = cleaned_data.get('gastos_fijos', Decimal('0'))
        ahorro = cleaned_data.get('ahorro_mensual', Decimal('0'))

        ingreso_total = ingreso + otros_ingresos

        # Validate gastos don't exceed ingresos
        if gastos > ingreso_total:
            raise forms.ValidationError(
                'Los gastos fijos no pueden ser mayores al ingreso total.'
            )

        # Validate ahorro + gastos don't exceed ingresos
        if (gastos + ahorro) > ingreso_total:
            raise forms.ValidationError(
                'La suma de gastos fijos y ahorro mensual no puede exceder el ingreso total. '
                f'Ingreso disponible: ${ingreso_total - gastos:.2f}'
            )

        return cleaned_data


class DeudaForm(forms.ModelForm):
    class Meta:
        model = Deuda
        fields = [
            'tipo', 'nombre', 'saldo_actual', 'pago_mensual',
            'tasa_interes', 'fecha_inicio', 'plazo_meses'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),
            'saldo_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'pago_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'tasa_interes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'plazo_meses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '600'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        saldo = cleaned_data.get('saldo_actual')
        pago = cleaned_data.get('pago_mensual')
        plazo = cleaned_data.get('plazo_meses')

        # Validate pago mensual is reasonable for saldo
        if saldo and pago and pago > saldo:
            raise forms.ValidationError(
                'El pago mensual no puede ser mayor al saldo actual de la deuda.'
            )

        # Warn if plazo * pago is much less than saldo (suspicious)
        if saldo and pago and plazo:
            total_pagos = pago * plazo
            if total_pagos < (saldo * Decimal('0.5')):  # Less than 50% of debt
                self.add_error('plazo_meses',
                    f'Advertencia: Con {plazo} meses de ${pago:.2f}, solo pagarías ${total_pagos:.2f} '
                    f'de los ${saldo:.2f} adeudados. Verifica los datos.'
                )

        return cleaned_data


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
