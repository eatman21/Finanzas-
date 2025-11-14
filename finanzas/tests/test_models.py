"""
Tests for finanzas models
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from finanzas.models.account import Account, Currency, AccountType
from finanzas.models.transaction import Transaction, Category, TransactionType
from finanzas.models.budget import Budget, BudgetPeriod
from finanzas.legacy_models import PerfilFinanciero, Deuda


class AccountModelTest(TestCase):
    """Test cases for Account model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.currency = Currency.objects.get(code='MXN')

    def test_account_creation(self):
        """Test creating an account"""
        account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type=AccountType.CHECKING,
            currency=self.currency,
            initial_balance=Decimal('1000.00')
        )
        self.assertEqual(account.name, 'Test Account')
        self.assertEqual(account.balance, Decimal('1000.00'))
        self.assertTrue(account.is_active)

    def test_account_str(self):
        """Test account string representation"""
        account = Account.objects.create(
            user=self.user,
            name='My Savings',
            account_type=AccountType.SAVINGS,
            currency=self.currency
        )
        self.assertEqual(str(account), 'My Savings')


class TransactionModelTest(TestCase):
    """Test cases for Transaction model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.currency = Currency.objects.get(code='MXN')
        self.account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type=AccountType.CHECKING,
            currency=self.currency,
            initial_balance=Decimal('1000.00')
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Groceries',
            category_type='expense'
        )

    def test_transaction_creation_income(self):
        """Test creating an income transaction"""
        transaction = Transaction.objects.create(
            account=self.account,
            transaction_type=TransactionType.INCOME,
            amount=Decimal('500.00'),
            description='Salary',
            category=self.category
        )
        self.assertEqual(transaction.amount, Decimal('500.00'))
        self.assertEqual(transaction.transaction_type, TransactionType.INCOME)

    def test_transaction_updates_account_balance(self):
        """Test that transactions update account balance"""
        initial_balance = self.account.balance

        # Create income transaction
        Transaction.objects.create(
            account=self.account,
            transaction_type=TransactionType.INCOME,
            amount=Decimal('500.00'),
            description='Bonus'
        )

        self.account.refresh_from_db()
        self.assertEqual(
            self.account.balance,
            initial_balance + Decimal('500.00')
        )


class CategoryModelTest(TestCase):
    """Test cases for Category model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_category_creation(self):
        """Test creating a category"""
        category = Category.objects.create(
            user=self.user,
            name='Food',
            category_type='expense',
            color='#FF5733'
        )
        self.assertEqual(category.name, 'Food')
        self.assertEqual(category.color, '#FF5733')
        self.assertTrue(category.is_active)

    def test_subcategory_creation(self):
        """Test creating a subcategory"""
        parent = Category.objects.create(
            user=self.user,
            name='Food',
            category_type='expense'
        )
        child = Category.objects.create(
            user=self.user,
            name='Groceries',
            category_type='expense',
            parent=parent
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.subcategories.all())


class LegacyPerfilFinancieroTest(TestCase):
    """Test cases for legacy PerfilFinanciero model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_perfil_creation(self):
        """Test creating a financial profile"""
        perfil = PerfilFinanciero.objects.create(
            usuario=self.user,
            ingreso_mensual=Decimal('15000.00'),
            otros_ingresos=Decimal('2000.00'),
            gastos_fijos=Decimal('8000.00')
        )
        self.assertEqual(perfil.ingreso_mensual, Decimal('15000.00'))
        self.assertTrue(perfil.ingreso_total > Decimal('15000.00'))

    def test_capacidad_ahorro(self):
        """Test savings capacity calculation"""
        perfil = PerfilFinanciero.objects.create(
            usuario=self.user,
            ingreso_mensual=Decimal('15000.00'),
            otros_ingresos=Decimal('0.00'),
            gastos_fijos=Decimal('8000.00')
        )
        expected_ahorro = Decimal('15000.00') - Decimal('8000.00')
        self.assertEqual(perfil.capacidad_ahorro, expected_ahorro)


class BudgetModelTest(TestCase):
    """Test cases for Budget model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_budget_creation(self):
        """Test creating a budget"""
        from datetime import date
        budget = Budget.objects.create(
            user=self.user,
            name='Monthly Budget',
            period=BudgetPeriod.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            total_amount=Decimal('10000.00')
        )
        self.assertEqual(budget.name, 'Monthly Budget')
        self.assertEqual(budget.total_amount, Decimal('10000.00'))
        self.assertTrue(budget.is_active)
