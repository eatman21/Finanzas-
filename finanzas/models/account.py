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
        """Recalculate current balance based on transactions - Thread-safe"""
        from django.db import transaction as db_transaction
        from django.core.cache import cache
        from .transaction import Transaction

        with db_transaction.atomic():
            # Lock the account row to prevent race conditions
            account = Account.objects.select_for_update().get(pk=self.pk)

            transactions = account.transactions.filter(is_cancelled=False)

            # Use single query with conditional aggregation
            aggregates = transactions.aggregate(
                income=models.Sum(
                    'amount',
                    filter=models.Q(transaction_type=Transaction.TransactionType.INCOME)
                ),
                expense=models.Sum(
                    'amount',
                    filter=models.Q(transaction_type=Transaction.TransactionType.EXPENSE)
                ),
                transfers_out=models.Sum(
                    'amount',
                    filter=models.Q(transaction_type=Transaction.TransactionType.TRANSFER)
                ),
            )

            income = aggregates['income'] or Decimal('0.00')
            expense = aggregates['expense'] or Decimal('0.00')
            transfers_out = aggregates['transfers_out'] or Decimal('0.00')

            transfers_in = account.incoming_transfers.filter(
                is_cancelled=False
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0.00')

            account.current_balance = (
                account.initial_balance +
                income -
                expense -
                transfers_out +
                transfers_in
            )
            account.save(update_fields=['current_balance'])

            # Invalidate cache
            cache.delete(f'account_summary_{account.id}')

    def get_summary(self):
        """Get cached summary of account transactions"""
        from django.core.cache import cache
        from django.db.models import Q, Sum
        from .transaction import Transaction

        cache_key = f'account_summary_{self.id}'
        summary = cache.get(cache_key)

        if summary is None:
            transactions = self.transactions.filter(is_cancelled=False)

            # Single optimized query with conditional aggregation
            aggregates = transactions.aggregate(
                total_income=Sum(
                    'amount',
                    filter=Q(transaction_type=Transaction.TransactionType.INCOME)
                ),
                total_expenses=Sum(
                    'amount',
                    filter=Q(transaction_type=Transaction.TransactionType.EXPENSE)
                ),
                total_transfers_out=Sum(
                    'amount',
                    filter=Q(transaction_type=Transaction.TransactionType.TRANSFER)
                ),
            )

            transfers_in = self.incoming_transfers.filter(
                is_cancelled=False
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            summary = {
                'total_income': aggregates['total_income'] or Decimal('0.00'),
                'total_expenses': aggregates['total_expenses'] or Decimal('0.00'),
                'total_transfers_out': aggregates['total_transfers_out'] or Decimal('0.00'),
                'total_transfers_in': transfers_in,
                'net_flow': (aggregates['total_income'] or Decimal('0.00')) -
                           (aggregates['total_expenses'] or Decimal('0.00')),
            }

            # Cache for 10 minutes
            from finanzas.constants import CACHE_ACCOUNT_SUMMARY
            cache.set(cache_key, summary, CACHE_ACCOUNT_SUMMARY)

        return summary

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:account_detail', kwargs={'pk': self.pk})

    @property
    def total_income(self):
        """Get total income for this account - Cached"""
        return self.get_summary()['total_income']

    @property
    def total_expenses(self):
        """Get total expenses for this account - Cached"""
        return self.get_summary()['total_expenses']

    @property
    def net_flow(self):
        """Get net cash flow (income - expenses) - Cached"""
        return self.get_summary()['net_flow']
