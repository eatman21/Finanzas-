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
    AccountSerializer, TransactionSerializer, CategorySerializer, BudgetSerializer
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
