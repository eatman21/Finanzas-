from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import QuerySet
from typing import Optional
from .models import PerfilFinanciero, Deuda, ObjetivoFinanciero, SimulacionCredito, Recomendacion
from .forms import PerfilFinancieroForm, DeudaForm, ObjetivoFinancieroForm, SimulacionCreditoForm


@login_required
def dashboard(request):
    """Vista principal del dashboard financiero"""
    try:
        perfil: Optional[PerfilFinanciero] = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        perfil = None

    context = {
        'perfil': perfil,
        # type: ignore
        'deudas': Deuda.objects.filter(perfil__usuario=request.user) if perfil else [],
        # type: ignore
        'objetivos': ObjetivoFinanciero.objects.filter(perfil__usuario=request.user, activo=True) if perfil else [],
        # type: ignore
        'simulaciones': SimulacionCredito.objects.filter(perfil__usuario=request.user)[:5] if perfil else [],
        # type: ignore
        'recomendaciones': Recomendacion.objects.filter(perfil__usuario=request.user, activa=True)[:3] if perfil else [],
    }
    return render(request, 'finanzas/dashboard.html', context)


@login_required
def calculadora_moderna(request):
    """Vista para la calculadora financiera moderna"""
    try:
        perfil: Optional[PerfilFinanciero] = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        perfil = None

    context = {
        'perfil': perfil,
    }
    return render(request, 'finanzas/calculadora_moderna.html', context)


@login_required
def perfil_financiero(request):
    """Vista para mostrar el perfil financiero del usuario"""
    try:
        perfil: PerfilFinanciero = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        return redirect('finanzas:editar_perfil')

    context = {
        'perfil': perfil,
        'deudas': perfil.deudas.all(),
        'objetivos': perfil.objetivos.filter(activo=True),
    }
    return render(request, 'finanzas/perfil_financiero.html', context)


@login_required
def editar_perfil(request):
    """Vista para crear o editar el perfil financiero"""
    try:
        perfil: Optional[PerfilFinanciero] = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        perfil = None

    if request.method == 'POST':
        form = PerfilFinancieroForm(request.POST, instance=perfil)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.save()
            messages.success(
                request, 'Perfil financiero actualizado correctamente.')
            return redirect('finanzas:perfil_financiero')
    else:
        form = PerfilFinancieroForm(instance=perfil)

    context = {
        'form': form,
        'perfil': perfil,
    }
    return render(request, 'finanzas/editar_perfil.html', context)


@login_required
def lista_deudas(request):
    """Vista para listar las deudas del usuario"""
    try:
        perfil: PerfilFinanciero = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
        deudas = perfil.deudas.all()
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        deudas = []

    context = {
        'deudas': deudas,
    }
    return render(request, 'finanzas/lista_deudas.html', context)


@login_required
def nueva_deuda(request):
    """Vista para crear una nueva deuda"""
    try:
        perfil: PerfilFinanciero = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        messages.error(request, 'Primero debes crear tu perfil financiero.')
        return redirect('finanzas:editar_perfil')

    if request.method == 'POST':
        form = DeudaForm(request.POST)
        if form.is_valid():
            deuda = form.save(commit=False)
            deuda.perfil = perfil
            deuda.save()
            messages.success(request, 'Deuda agregada correctamente.')
            return redirect('finanzas:lista_deudas')
    else:
        form = DeudaForm()

    context = {
        'form': form,
    }
    return render(request, 'finanzas/nueva_deuda.html', context)


@login_required
def editar_deuda(request, pk):
    """Vista para editar una deuda existente"""
    deuda = get_object_or_404(Deuda, pk=pk, perfil__usuario=request.user)

    if request.method == 'POST':
        form = DeudaForm(request.POST, instance=deuda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deuda actualizada correctamente.')
            return redirect('finanzas:lista_deudas')
    else:
        form = DeudaForm(instance=deuda)

    context = {
        'form': form,
        'deuda': deuda,
    }
    return render(request, 'finanzas/editar_deuda.html', context)


@login_required
@require_POST
def eliminar_deuda(request, pk):
    """Vista para eliminar una deuda"""
    deuda = get_object_or_404(Deuda, pk=pk, perfil__usuario=request.user)
    deuda.delete()
    messages.success(request, 'Deuda eliminada correctamente.')
    return redirect('finanzas:lista_deudas')


@login_required
def lista_objetivos(request):
    """Vista para listar los objetivos financieros del usuario"""
    try:
        perfil: PerfilFinanciero = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
        objetivos = perfil.objetivos.all()
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        objetivos = []

    context = {
        'objetivos': objetivos,
    }
    return render(request, 'finanzas/lista_objetivos.html', context)


@login_required
def nuevo_objetivo(request):
    """Vista para crear un nuevo objetivo financiero"""
    try:
        perfil: PerfilFinanciero = PerfilFinanciero.objects.get(
            usuario=request.user)  # type: ignore
    except PerfilFinanciero.DoesNotExist:  # type: ignore
        messages.error(request, 'Primero debes crear tu perfil financiero.')
        return redirect('finanzas:editar_perfil')

    if request.method == 'POST':
        form = ObjetivoFinancieroForm(request.POST)
        if form.is_valid():
            objetivo = form.save(commit=False)
            objetivo.perfil = perfil
            objetivo.save()
            messages.success(
                request, 'Objetivo financiero creado correctamente.')
            return redirect('finanzas:lista_objetivos')
    else:
        form = ObjetivoFinancieroForm()

    context = {
        'form': form,
    }
    return render(request, 'finanzas/nuevo_objetivo.html', context)


@login_required
def editar_objetivo(request, pk):
    """Vista para editar un objetivo financiero existente"""
    objetivo = get_object_or_404(
        ObjetivoFinanciero, pk=pk, perfil__usuario=request.user)

    if request.method == 'POST':
        form = ObjetivoFinancieroForm(request.POST, instance=objetivo)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Objetivo financiero actualizado correctamente.')
            return redirect('finanzas:lista_objetivos')
    else:
        form = ObjetivoFinancieroForm(instance=objetivo)

    context = {
        'form': form,
        'objetivo': objetivo,
    }
    return render(request, 'finanzas/editar_objetivo.html', context)


@login_required
@require_POST
def eliminar_objetivo(request, pk):
    """Vista para eliminar un objetivo financiero"""
    objetivo = get_object_or_404(
        ObjetivoFinanciero, pk=pk, perfil__usuario=request.user)
    objetivo.delete()
    messages.success(request, 'Objetivo financiero eliminado correctamente.')
    return redirect('finanzas:lista_objetivos')


@login_required
def lista_simulaciones(request):
    """Vista para listar las simulaciones de crédito del usuario"""
    try:
        perfil = get_object_or_404(PerfilFinanciero, usuario=request.user)
        simulaciones = perfil.simulaciones.all()
    except PerfilFinanciero.DoesNotExist:
        simulaciones = []

    context = {
        'simulaciones': simulaciones,
    }
    return render(request, 'finanzas/lista_simulaciones.html', context)


@login_required
def nueva_simulacion(request):
    """Vista para crear una nueva simulación de crédito"""
    try:
        perfil = get_object_or_404(PerfilFinanciero, usuario=request.user)
    except PerfilFinanciero.DoesNotExist:
        messages.error(request, 'Primero debes crear tu perfil financiero.')
        return redirect('finanzas:editar_perfil')

    if request.method == 'POST':
        form = SimulacionCreditoForm(request.POST)
        if form.is_valid():
            simulacion = form.save(commit=False)
            simulacion.perfil = perfil
            simulacion.save()
            messages.success(
                request, 'Simulación de crédito creada correctamente.')
            return redirect('finanzas:detalle_simulacion', pk=simulacion.pk)
    else:
        form = SimulacionCreditoForm()

    context = {
        'form': form,
    }
    return render(request, 'finanzas/nueva_simulacion.html', context)


@login_required
def detalle_simulacion(request, pk):
    """Vista para mostrar los detalles de una simulación de crédito"""
    simulacion = get_object_or_404(
        SimulacionCredito, pk=pk, perfil__usuario=request.user)

    context = {
        'simulacion': simulacion,
        # Primeros 12 meses
        'tabla_amortizacion': simulacion.tabla_amortizacion()[:12],
    }
    return render(request, 'finanzas/detalle_simulacion.html', context)


@login_required
@require_POST
def eliminar_simulacion(request, pk):
    """Vista para eliminar una simulación de crédito"""
    simulacion = get_object_or_404(
        SimulacionCredito, pk=pk, perfil__usuario=request.user)
    simulacion.delete()
    messages.success(request, 'Simulación de crédito eliminada correctamente.')
    return redirect('finanzas:lista_simulaciones')


@login_required
def lista_recomendaciones(request):
    """Vista para listar las recomendaciones del usuario"""
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
        recomendaciones = perfil.recomendaciones.filter(activa=True)
    except PerfilFinanciero.DoesNotExist:
        recomendaciones = []

    context = {
        'recomendaciones': recomendaciones,
    }
    return render(request, 'finanzas/lista_recomendaciones.html', context)
