"""
Tests for finanzas forms
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from finanzas.forms import PerfilFinancieroForm, DeudaForm
from finanzas.legacy_models import PerfilFinanciero


class PerfilFinancieroFormTest(TestCase):
    """Test cases for PerfilFinanciero form"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_valid_perfil_form(self):
        """Test that valid data creates a valid form"""
        data = {
            'ingreso_mensual': '15000.00',
            'otros_ingresos': '2000.00',
            'gastos_fijos': '8000.00',
            'score_crediticio': 700
        }
        form = PerfilFinancieroForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_perfil_form_negative_income(self):
        """Test that negative income is invalid"""
        data = {
            'ingreso_mensual': '-15000.00',
            'otros_ingresos': '2000.00',
            'gastos_fijos': '8000.00',
            'score_crediticio': 700
        }
        form = PerfilFinancieroForm(data=data)
        self.assertFalse(form.is_valid())


class DeudaFormTest(TestCase):
    """Test cases for Deuda form"""

    def test_valid_deuda_form(self):
        """Test that valid debt data creates a valid form"""
        data = {
            'tipo': 'credito_personal',
            'nombre': 'Personal Loan',
            'saldo_actual': '50000.00',
            'pago_mensual': '2500.00',
            'tasa_interes': '12.5',
            'plazo_meses': 24
        }
        form = DeudaForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_deuda_form_zero_balance(self):
        """Test that zero balance is invalid"""
        data = {
            'tipo': 'credito_personal',
            'nombre': 'Personal Loan',
            'saldo_actual': '0.00',
            'pago_mensual': '2500.00',
            'tasa_interes': '12.5',
            'plazo_meses': 24
        }
        form = DeudaForm(data=data)
        self.assertFalse(form.is_valid())
