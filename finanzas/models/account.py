from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _


class AccountType(models.TextChoices):
    CHECKING = 'CHECKING', _('Cuenta de Cheques')
    SAVINGS = 'SAVINGS', _('Cuenta de Ahorros')
    CREDIT_CARD = 'CREDIT_CARD', _('Tarjeta de Crédito')
    INVESTMENT = 'INVESTMENT', _('Inversión')
    LOAN = 'LOAN', _('Préstamo')
    CASH = 'CASH', _('Efectivo')


class Currency(models.TextChoices):
    MXN = 'MXN', _('Peso Mexicano')
    USD = 'USD', _('Dólar Estadounidense')
    EUR = 'EUR', _('Euro')


class Account(models.Model):
    """Financial account model"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name=_('Usuario')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre de la Cuenta')
    )
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CHECKING,
        verbose_name=_('Tipo de Cuenta')
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.MXN,
        verbose_name=_('Moneda')
    )
    initial_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Saldo Inicial')
    )
    current_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Saldo Actual')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activa')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de Creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Actualización')
    )

    class Meta:
        verbose_name = _('Cuenta')
        verbose_name_plural = _('Cuentas')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['account_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    def update_balance(self):
        """Recalculate current balance based on transactions"""
        from .transaction import Transaction

        transactions = self.transactions.filter(is_cancelled=False)
        income = transactions.filter(
            transaction_type=Transaction.TransactionType.INCOME
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        expense = transactions.filter(
            transaction_type=Transaction.TransactionType.EXPENSE
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        transfers_out = transactions.filter(
            transaction_type=Transaction.TransactionType.TRANSFER
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        transfers_in = self.incoming_transfers.filter(
            is_cancelled=False
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        self.current_balance = (
            self.initial_balance +
            income -
            expense -
            transfers_out +
            transfers_in
        )
        self.save(update_fields=['current_balance'])

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:account_detail', kwargs={'pk': self.pk})

    @property
    def total_income(self):
        """Get total income for this account"""
        from .transaction import Transaction
        return self.transactions.filter(
            transaction_type=Transaction.TransactionType.INCOME,
            is_cancelled=False
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    @property
    def total_expenses(self):
        """Get total expenses for this account"""
        from .transaction import Transaction
        return self.transactions.filter(
            transaction_type=Transaction.TransactionType.EXPENSE,
            is_cancelled=False
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    @property
    def net_flow(self):
        """Get net cash flow (income - expenses)"""
        return self.total_income - self.total_expenses
