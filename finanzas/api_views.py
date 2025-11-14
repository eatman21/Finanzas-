from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, F
from django.shortcuts import get_object_or_404
from .legacy_models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito, Recomendacion
from .models.account import Account
from .models.transaction import Transaction, Category
from .models.budget import Budget
from .serializers import (
    PerfilFinancieroSerializer, DeudaSerializer, ObjetivoFinancieroSerializer,
    SimulacionCreditoSerializer, RecomendacionSerializer,
    AccountSerializer, TransactionSerializer, CategorySerializer, BudgetSerializer,
    DashboardSerializer
)


class PerfilFinancieroViewSet(viewsets.ModelViewSet):
    serializer_class = PerfilFinancieroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PerfilFinanciero.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard summary data"""
        try:
            perfil = PerfilFinanciero.objects.get(usuario=request.user)
        except PerfilFinanciero.DoesNotExist:
            return Response(
                {'error': 'Perfil financiero no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate totals
        total_deudas = perfil.deudas.aggregate(
            total=Sum('saldo_actual')
        )['total'] or 0

        total_objetivos = perfil.objetivos.filter(activo=True).aggregate(
            total=Sum('monto_objetivo')
        )['total'] or 0

        # Calculate debt utilization percentage
        capacidad_utilizada = 0
        if perfil.capacidad_endeudamiento > 0:
            total_pagos_mensuales = perfil.deudas.aggregate(
                total=Sum('pago_mensual')
            )['total'] or 0
            capacidad_utilizada = (
                total_pagos_mensuales / perfil.capacidad_endeudamiento) * 100

        dashboard_data = {
            'perfil': perfil,
            'deudas': perfil.deudas.all(),
            'objetivos': perfil.objetivos.filter(activo=True),
            'simulaciones': perfil.simulaciones.all()[:5],
            'recomendaciones': perfil.recomendaciones.filter(activa=True)[:3],
            'total_deudas': total_deudas,
            'total_objetivos': total_objetivos,
            'capacidad_endeudamiento_utilizada': capacidad_utilizada,
        }

        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data)


class DeudaViewSet(viewsets.ModelViewSet):
    serializer_class = DeudaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Deuda.objects.filter(perfil__usuario=self.request.user)

    def perform_create(self, serializer):
        perfil = get_object_or_404(PerfilFinanciero, usuario=self.request.user)
        serializer.save(perfil=perfil)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get debt summary statistics"""
        queryset = self.get_queryset()

        total_deudas = queryset.aggregate(
            total=Sum('saldo_actual')
        )['total'] or 0

        total_pagos_mensuales = queryset.aggregate(
            total=Sum('pago_mensual')
        )['total'] or 0

        tipos_deuda = queryset.values('tipo').annotate(
            count=Count('id'),
            total_saldo=Sum('saldo_actual')
        )

        return Response({
            'total_deudas': total_deudas,
            'total_pagos_mensuales': total_pagos_mensuales,
            'cantidad_deudas': queryset.count(),
            'tipos_deuda': tipos_deuda,
        })


class ObjetivoFinancieroViewSet(viewsets.ModelViewSet):
    serializer_class = ObjetivoFinancieroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ObjetivoFinanciero.objects.filter(perfil__usuario=self.request.user)

    def perform_create(self, serializer):
        perfil = get_object_or_404(PerfilFinanciero, usuario=self.request.user)
        serializer.save(perfil=perfil)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial goals summary"""
        queryset = self.get_queryset().filter(activo=True)

        total_objetivos = queryset.aggregate(
            total=Sum('monto_objetivo')
        )['total'] or 0

        total_ahorro_requerido = queryset.aggregate(
            total=Sum('ahorro_mensual_requerido')
        )['total'] or 0

        tipos_objetivo = queryset.values('tipo').annotate(
            count=Count('id'),
            total_monto=Sum('monto_objetivo')
        )

        return Response({
            'total_objetivos': total_objetivos,
            'total_ahorro_requerido': total_ahorro_requerido,
            'cantidad_objetivos': queryset.count(),
            'tipos_objetivo': tipos_objetivo,
        })


class SimulacionCreditoViewSet(viewsets.ModelViewSet):
    serializer_class = SimulacionCreditoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SimulacionCredito.objects.filter(perfil__usuario=self.request.user)

    def perform_create(self, serializer):
        perfil = get_object_or_404(PerfilFinanciero, usuario=self.request.user)
        serializer.save(perfil=perfil)

    @action(detail=True, methods=['get'])
    def amortizacion(self, request, pk=None):
        """Get amortization table for a credit simulation"""
        simulacion = self.get_object()
        tabla_amortizacion = simulacion.tabla_amortizacion()

        return Response({
            'simulacion': SimulacionCreditoSerializer(simulacion).data,
            'tabla_amortizacion': tabla_amortizacion,
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get credit simulations summary"""
        queryset = self.get_queryset()

        simulaciones_viables = queryset.filter(
            pago_mensual__lte=F('perfil__capacidad_endeudamiento')
        ).count()

        total_simulaciones = queryset.count()

        return Response({
            'total_simulaciones': total_simulaciones,
            'simulaciones_viables': simulaciones_viables,
            'porcentaje_viables': (simulaciones_viables / total_simulaciones * 100) if total_simulaciones > 0 else 0,
        })


class RecomendacionViewSet(viewsets.ModelViewSet):
    serializer_class = RecomendacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recomendacion.objects.filter(perfil__usuario=self.request.user)

    def perform_create(self, serializer):
        perfil = get_object_or_404(PerfilFinanciero, usuario=self.request.user)
        serializer.save(perfil=perfil)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active recommendations"""
        queryset = self.get_queryset().filter(activa=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Modern Financial Management ViewSets

class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user accounts"""
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_active=True).select_related('currency')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get accounts summary"""
        queryset = self.get_queryset()

        total_balance = sum(account.balance for account in queryset)
        by_type = {}
        for account in queryset:
            if account.account_type not in by_type:
                by_type[account.account_type] = {
                    'count': 0,
                    'total_balance': 0
                }
            by_type[account.account_type]['count'] += 1
            by_type[account.account_type]['total_balance'] += float(account.balance)

        return Response({
            'total_accounts': queryset.count(),
            'total_balance': total_balance,
            'by_type': by_type,
        })


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user
        ).select_related('account', 'category').order_by('-date', '-created_at')

    def perform_create(self, serializer):
        # Validate that the account belongs to the user
        account = serializer.validated_data.get('account')
        if account.user != self.request.user:
            raise permissions.PermissionDenied("You don't have permission to access this account")
        serializer.save()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transactions summary"""
        queryset = self.get_queryset()

        # Get query parameters for filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        total_income = queryset.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_expense = queryset.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': total_income - total_expense,
            'total_transactions': queryset.count(),
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing transaction categories"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user, is_active=True).prefetch_related('subcategories')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing budgets"""
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).prefetch_related('categories')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get budget progress details"""
        budget = self.get_object()

        return Response({
            'budget': BudgetSerializer(budget).data,
            'spent_amount': budget.spent_amount,
            'remaining_amount': budget.remaining_amount,
            'spent_percentage': budget.spent_percentage,
            'is_over_budget': budget.spent_percentage > 100,
        })
