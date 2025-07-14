from django import forms
from .models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito


class PerfilFinancieroForm(forms.ModelForm):
    class Meta:
        model = PerfilFinanciero
        fields = [
            'ingreso_mensual',
            'otros_ingresos',
            'gastos_fijos',
            'ahorro_mensual',
            'ahorro_actual',
            'score_crediticio'
        ]
        widgets = {
            'ingreso_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'otros_ingresos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gastos_fijos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ahorro_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ahorro_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'score_crediticio': forms.NumberInput(attrs={'class': 'form-control', 'min': '300', 'max': '850'}),
        }


class DeudaForm(forms.ModelForm):
    class Meta:
        model = Deuda
        fields = [
            'tipo',
            'nombre',
            'saldo_actual',
            'pago_mensual',
            'tasa_interes',
            'fecha_inicio',
            'plazo_meses'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'saldo_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pago_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tasa_interes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plazo_meses': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ObjetivoFinancieroForm(forms.ModelForm):
    class Meta:
        model = ObjetivoFinanciero
        fields = [
            'tipo',
            'nombre',
            'monto_objetivo',
            'plazo_meses',
            'activo'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_objetivo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'plazo_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SimulacionCreditoForm(forms.ModelForm):
    class Meta:
        model = SimulacionCredito
        fields = [
            'tipo',
            'nombre',
            'valor_propiedad',
            'enganche_porcentaje',
            'tasa_interes_anual',
            'plazo_anos',
            'gastos_adicionales'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_propiedad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'enganche_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tasa_interes_anual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'plazo_anos': forms.NumberInput(attrs={'class': 'form-control'}),
            'gastos_adicionales': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
