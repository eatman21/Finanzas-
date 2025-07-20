from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder


class ReportType(models.TextChoices):
    INCOME_EXPENSE = 'INCOME_EXPENSE', _('Ingresos vs Gastos')
    CATEGORY_ANALYSIS = 'CATEGORY_ANALYSIS', _('Análisis por Categoría')
    ACCOUNT_BALANCE = 'ACCOUNT_BALANCE', _('Balance de Cuentas')
    BUDGET_VS_ACTUAL = 'BUDGET_VS_ACTUAL', _('Presupuesto vs Real')
    CASH_FLOW = 'CASH_FLOW', _('Flujo de Efectivo')
    NET_WORTH = 'NET_WORTH', _('Patrimonio Neto')


class Report(models.Model):
    """Financial report model"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('Usuario')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre del Reporte')
    )
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        verbose_name=_('Tipo de Reporte')
    )
    start_date = models.DateField(
        verbose_name=_('Fecha de Inicio')
    )
    end_date = models.DateField(
        verbose_name=_('Fecha de Fin')
    )
    parameters = models.JSONField(
        encoder=DjangoJSONEncoder,
        default=dict,
        blank=True,
        verbose_name=_('Parámetros')
    )
    data = models.JSONField(
        encoder=DjangoJSONEncoder,
        default=dict,
        blank=True,
        verbose_name=_('Datos del Reporte')
    )
    is_saved = models.BooleanField(
        default=False,
        verbose_name=_('Guardado')
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
        verbose_name = _('Reporte')
        verbose_name_plural = _('Reportes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'report_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

    def generate_report(self):
        """Generate report data based on type and parameters"""
        if self.report_type == ReportType.INCOME_EXPENSE:
            self._generate_income_expense_report()
        elif self.report_type == ReportType.CATEGORY_ANALYSIS:
            self._generate_category_analysis_report()
        elif self.report_type == ReportType.ACCOUNT_BALANCE:
            self._generate_account_balance_report()
        elif self.report_type == ReportType.BUDGET_VS_ACTUAL:
            self._generate_budget_vs_actual_report()
        elif self.report_type == ReportType.CASH_FLOW:
            self._generate_cash_flow_report()
        elif self.report_type == ReportType.NET_WORTH:
            self._generate_net_worth_report()

        self.save()

    def _generate_income_expense_report(self):
        """Generate income vs expense report"""
        from .transaction import Transaction

        transactions = Transaction.objects.filter(
            user=self.user,
            date__range=[self.start_date, self.end_date],
            is_cancelled=False
        )

        income = transactions.filter(
            transaction_type=Transaction.TransactionType.INCOME
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        expenses = transactions.filter(
            transaction_type=Transaction.TransactionType.EXPENSE
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        self.data = {
            'income': float(income),
            'expenses': float(expenses),
            'net_income': float(income - expenses),
            'period': f"{self.start_date} - {self.end_date}",
        }

    def _generate_category_analysis_report(self):
        """Generate category analysis report"""
        from .transaction import Transaction

        transactions = Transaction.objects.filter(
            user=self.user,
            date__range=[self.start_date, self.end_date],
            is_cancelled=False
        ).values('category__name').annotate(
            total=models.Sum('amount'),
            count=models.Count('id')
        ).order_by('-total')

        self.data = {
            'categories': list(transactions),
            'total_transactions': sum(item['count'] for item in transactions),
            'period': f"{self.start_date} - {self.end_date}",
        }

    def _generate_account_balance_report(self):
        """Generate account balance report"""
        from .account import Account

        accounts = Account.objects.filter(
            user=self.user,
            is_active=True
        ).values('name', 'account_type', 'current_balance', 'currency')

        self.data = {
            'accounts': list(accounts),
            'total_balance': sum(float(acc['current_balance']) for acc in accounts),
            'account_count': len(accounts),
        }

    def _generate_budget_vs_actual_report(self):
        """Generate budget vs actual report"""
        from .budget import Budget

        budgets = Budget.objects.filter(
            user=self.user,
            is_active=True,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )

        budget_data = []
        for budget in budgets:
            budget_data.append({
                'name': budget.name,
                'budgeted': float(budget.total_amount),
                'actual': float(budget.spent_amount),
                'variance': float(budget.remaining_amount),
                'variance_percentage': float(budget.spent_percentage),
            })

        self.data = {
            'budgets': budget_data,
            'period': f"{self.start_date} - {self.end_date}",
        }

    def _generate_cash_flow_report(self):
        """Generate cash flow report"""
        from .transaction import Transaction

        transactions = Transaction.objects.filter(
            user=self.user,
            date__range=[self.start_date, self.end_date],
            is_cancelled=False
        ).order_by('date')

        cash_flow_data = []
        running_balance = 0

        for transaction in transactions:
            if transaction.transaction_type == Transaction.TransactionType.INCOME:
                running_balance += float(transaction.amount)
            elif transaction.transaction_type == Transaction.TransactionType.EXPENSE:
                running_balance -= float(transaction.amount)

            cash_flow_data.append({
                'date': transaction.date.isoformat(),
                'description': transaction.description,
                'amount': float(transaction.amount),
                'type': transaction.transaction_type,
                'running_balance': running_balance,
            })

        self.data = {
            'cash_flow': cash_flow_data,
            'final_balance': running_balance,
            'period': f"{self.start_date} - {self.end_date}",
        }

    def _generate_net_worth_report(self):
        """Generate net worth report"""
        from .account import Account

        accounts = Account.objects.filter(
            user=self.user,
            is_active=True
        )

        total_assets = sum(
            float(acc.current_balance)
            for acc in accounts
            if acc.account_type in [Account.AccountType.CHECKING, Account.AccountType.SAVINGS, Account.AccountType.INVESTMENT]
        )

        total_liabilities = sum(
            float(acc.current_balance)
            for acc in accounts
            if acc.account_type in [Account.AccountType.CREDIT_CARD, Account.AccountType.LOAN]
        )

        net_worth = total_assets - total_liabilities

        self.data = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'net_worth': net_worth,
            'date': self.end_date.isoformat(),
        }

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:report_detail', kwargs={'pk': self.pk})
