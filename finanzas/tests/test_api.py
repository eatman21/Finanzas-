"""
Tests for finanzas API views
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from finanzas.models.account import Account, Currency, AccountType
from finanzas.legacy_models import PerfilFinanciero


class AccountAPITest(TestCase):
    """Test cases for Account API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.currency = Currency.objects.get(code='MXN')

    def test_account_list_authenticated(self):
        """Test getting account list when authenticated"""
        Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type=AccountType.CHECKING,
            currency=self.currency
        )

        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_account_list_unauthenticated(self):
        """Test that unauthenticated users cannot access accounts"""
        self.client.logout()
        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_account_create(self):
        """Test creating an account via API"""
        data = {
            'name': 'New Account',
            'account_type': AccountType.SAVINGS,
            'currency': self.currency.id,
            'initial_balance': '1000.00'
        }
        response = self.client.post('/api/accounts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)


class PerfilFinancieroAPITest(TestCase):
    """Test cases for PerfilFinanciero API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_perfil_creation(self):
        """Test creating a financial profile via API"""
        data = {
            'ingreso_mensual': '15000.00',
            'otros_ingresos': '2000.00',
            'gastos_fijos': '8000.00',
            'score_crediticio': 700
        }
        response = self.client.post('/api/perfiles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PerfilFinanciero.objects.count(), 1)

    def test_perfil_list_only_shows_own_profile(self):
        """Test that users only see their own profile"""
        # Create another user with a profile
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123'
        )
        PerfilFinanciero.objects.create(
            usuario=other_user,
            ingreso_mensual=Decimal('10000.00')
        )

        # Create profile for current user
        PerfilFinanciero.objects.create(
            usuario=self.user,
            ingreso_mensual=Decimal('15000.00')
        )

        response = self.client.get('/api/perfiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            Decimal(response.data['results'][0]['ingreso_mensual']),
            Decimal('15000.00')
        )


class TransactionAPITest(TestCase):
    """Test cases for Transaction API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.currency = Currency.objects.get(code='MXN')
        self.account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type=AccountType.CHECKING,
            currency=self.currency,
            initial_balance=Decimal('1000.00')
        )

    def test_transaction_summary(self):
        """Test transaction summary endpoint"""
        response = self.client.get('/api/transactions/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expense', response.data)
        self.assertIn('net_balance', response.data)
