from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from .account import Account


class Category(models.Model):
    """Transaction category"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Nombre')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Nombre del ícono (ej: fas fa-shopping-cart)'),
        verbose_name=_('Ícono')
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text=_('Color en formato hexadecimal'),
        verbose_name=_('Color')
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name=_('Categoría Padre')
    )
    is_income = models.BooleanField(
        default=False,
        verbose_name=_('Es Ingreso')
    )
    is_expense = models.BooleanField(
        default=True,
        verbose_name=_('Es Gasto')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Transaction(models.Model):
    """Financial transaction model"""

    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', _('Ingreso')
        EXPENSE = 'EXPENSE', _('Gasto')
        TRANSFER = 'TRANSFER', _('Transferencia')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('Usuario')
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('Cuenta')
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        verbose_name=_('Tipo de Transacción')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_('Categoría')
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Monto')
    )
    description = models.CharField(
        max_length=200,
        verbose_name=_('Descripción')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas')
    )
    date = models.DateField(
        verbose_name=_('Fecha')
    )
    is_recurring = models.BooleanField(
        default=False,
        verbose_name=_('Es Recurrente')
    )
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name=_('Cancelada')
    )
    # For transfers
    destination_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='incoming_transfers',
        verbose_name=_('Cuenta Destino')
    )
    # Attachments
    receipt = models.FileField(
        upload_to='receipts/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_('Recibo')
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
        verbose_name = _('Transacción')
        verbose_name_plural = _('Transacciones')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['account', 'transaction_type']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.description} - ${self.amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_amount = None

        if not is_new:
            old_instance = Transaction.objects.get(pk=self.pk)
            old_amount = old_instance.amount
            old_type = old_instance.transaction_type

        # Save the transaction
        super().save(*args, **kwargs)

        # Update account balances
        if is_new:
            # New transaction
            self._update_account_balance(
                self.account, self.amount, self.transaction_type, is_new=True)
            if self.transaction_type == self.TransactionType.TRANSFER and self.destination_account:
                self._update_account_balance(
                    self.destination_account, self.amount, self.TransactionType.INCOME, is_new=True)
        else:
            # Updated transaction
            if old_amount != self.amount or old_type != self.transaction_type:
                # Revert old transaction
                self._update_account_balance(
                    self.account, old_amount, old_type, is_revert=True)
                # Apply new transaction
                self._update_account_balance(
                    self.account, self.amount, self.transaction_type, is_new=True)

                # Handle transfer destination account
                if self.transaction_type == self.TransactionType.TRANSFER and self.destination_account:
                    self._update_account_balance(
                        self.destination_account, self.amount, self.TransactionType.INCOME, is_new=True)

    def delete(self, *args, **kwargs):
        # Revert account balances before deletion
        self._update_account_balance(
            self.account, self.amount, self.transaction_type, is_revert=True)
        if self.transaction_type == self.TransactionType.TRANSFER and self.destination_account:
            self._update_account_balance(
                self.destination_account, self.amount, self.TransactionType.INCOME, is_revert=True)

        super().delete(*args, **kwargs)

    def _update_account_balance(self, account, amount, transaction_type, is_new=False, is_revert=False):
        """Update account balance based on transaction"""
        if not amount:
            return

        multiplier = 1 if is_new else -1
        if is_revert:
            multiplier *= -1

        if transaction_type == self.TransactionType.INCOME:
            account.current_balance += amount * multiplier
        elif transaction_type == self.TransactionType.EXPENSE:
            account.current_balance -= amount * multiplier
        elif transaction_type == self.TransactionType.TRANSFER:
            # For transfers, we only update the source account here
            # Destination account is handled separately
            account.current_balance -= amount * multiplier

        account.save(update_fields=['current_balance'])

    @property
    def is_income(self):
        return self.transaction_type == self.TransactionType.INCOME

    @property
    def is_expense(self):
        return self.transaction_type == self.TransactionType.EXPENSE

    @property
    def is_transfer(self):
        return self.transaction_type == self.TransactionType.TRANSFER

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:transaction_detail', kwargs={'pk': self.pk})
