from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from .transaction import Category


class BudgetPeriod(models.TextChoices):
    MONTHLY = 'MONTHLY', _('Mensual')
    QUARTERLY = 'QUARTERLY', _('Trimestral')
    YEARLY = 'YEARLY', _('Anual')


class Budget(models.Model):
    """Budget model for financial planning"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name=_('Usuario')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre del Presupuesto')
    )
    period = models.CharField(
        max_length=10,
        choices=BudgetPeriod.choices,
        default=BudgetPeriod.MONTHLY,
        verbose_name=_('Período')
    )
    start_date = models.DateField(
        verbose_name=_('Fecha de Inicio')
    )
    end_date = models.DateField(
        verbose_name=_('Fecha de Fin')
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Monto Total')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo')
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
        verbose_name = _('Presupuesto')
        verbose_name_plural = _('Presupuestos')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_period_display()})"

    @property
    def spent_amount(self):
        """Get total amount spent in this budget period"""
        from .transaction import Transaction
        return Transaction.objects.filter(
            user=self.user,
            transaction_type=Transaction.TransactionType.EXPENSE,
            date__range=[self.start_date, self.end_date],
            is_cancelled=False,
            category__in=self.categories.values_list('category', flat=True)
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    @property
    def remaining_amount(self):
        """Get remaining budget amount"""
        return self.total_amount - self.spent_amount

    @property
    def spent_percentage(self):
        """Get percentage of budget spent"""
        if self.total_amount == 0:
            return 0
        return (self.spent_amount / self.total_amount) * 100

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:budget_detail', kwargs={'pk': self.pk})


class BudgetCategory(models.Model):
    """Budget allocation by category"""
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name=_('Presupuesto')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_('Categoría')
    )
    allocated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Monto Asignado')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas')
    )

    class Meta:
        verbose_name = _('Categoría de Presupuesto')
        verbose_name_plural = _('Categorías de Presupuesto')
        unique_together = ['budget', 'category']

    def __str__(self):
        return f"{self.category.name} - ${self.allocated_amount}"

    @property
    def spent_amount(self):
        """Get amount spent in this category for this budget period"""
        from .transaction import Transaction
        return Transaction.objects.filter(
            user=self.budget.user,
            category=self.category,
            transaction_type=Transaction.TransactionType.EXPENSE,
            date__range=[self.budget.start_date, self.budget.end_date],
            is_cancelled=False
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    @property
    def remaining_amount(self):
        """Get remaining amount for this category"""
        return self.allocated_amount - self.spent_amount

    @property
    def spent_percentage(self):
        """Get percentage of category budget spent"""
        if self.allocated_amount == 0:
            return 0
        return (self.spent_amount / self.allocated_amount) * 100
