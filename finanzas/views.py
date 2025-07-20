from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.db.models import Sum, Q, QuerySet
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List

# Import your models
from .legacy_models import (
    PerfilFinanciero,
    Deuda,
    ObjetivoFinanciero,
    SimulacionCredito,
    Recomendacion
)
from .models.account import Account
from .models.transaction import Transaction, Category
from .models.budget import Budget
from .forms import (
    PerfilFinancieroForm,
    DeudaForm,
    ObjetivoFinancieroForm,
    SimulacionCreditoForm
)


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Vista principal del dashboard financiero"""
    perfil = None
    deudas = []
    objetivos = []
    simulaciones = []
    recomendaciones = []

    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
        if perfil:
            deudas = Deuda.objects.filter(perfil=perfil)
            objetivos = ObjetivoFinanciero.objects.filter(
                perfil=perfil,
                activo=True
            )
            simulaciones = SimulacionCredito.objects.filter(
                perfil=perfil
            ).order_by('-fecha_simulacion')[:5]
            recomendaciones = Recomendacion.objects.filter(
                perfil=perfil,
                activa=True
            ).order_by('-fecha_creacion')[:3]
    except PerfilFinanciero.DoesNotExist:
        # It's okay if profile doesn't exist, we'll show empty data
        pass

    # Get account summary if using new models
    accounts_summary = {}
    if request.user.is_authenticated:
        accounts = Account.objects.filter(user=request.user, is_active=True)
        total_balance = accounts.aggregate(
            total=Sum('current_balance')
        )['total'] or Decimal('0.00')
        accounts_summary = {
            'accounts': accounts,
            'total_balance': total_balance,
        }

    # Get recent transactions
    recent_transactions = []
    if request.user.is_authenticated:
        recent_transactions = Transaction.objects.filter(
            user=request.user,
            is_cancelled=False
        ).select_related('account', 'category').order_by('-date', '-created_at')[:10]

    # Get budget alerts
    budget_alerts = []
    if request.user.is_authenticated:
        active_budgets = Budget.objects.filter(
            user=request.user,
            is_active=True
        )
        for budget in active_budgets:
            if budget.spent_percentage > 80:  # Alert if over 80% used
                budget_alerts.append({
                    'budget': budget,
                    'percentage_used': budget.spent_percentage,
                    'remaining': budget.remaining_amount,
                })

    context: Dict[str, Any] = {
        'perfil': perfil,
        'deudas': deudas,
        'objetivos': objetivos,
        'simulaciones': simulaciones,
        'recomendaciones': recomendaciones,
        'accounts_summary': accounts_summary,
        'recent_transactions': recent_transactions,
        'budget_alerts': budget_alerts[:3],  # Show only top 3 alerts
    }

    return render(request, 'finanzas/dashboard.html', context)


@login_required
def calculadora_moderna(request: HttpRequest) -> HttpResponse:
    """Vista para la calculadora financiera moderna"""
    perfil = None
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
    except PerfilFinanciero.DoesNotExist:
        pass

    context: Dict[str, Any] = {
        'perfil': perfil,
    }
    return render(request, 'finanzas/calculadora_moderna.html', context)


@login_required
def perfil_financiero(request: HttpRequest) -> HttpResponse:
    """Vista para mostrar el perfil financiero del usuario"""
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
    except PerfilFinanciero.DoesNotExist:
        messages.info(
            request,
            'Aún no has creado tu perfil financiero. Por favor, complétalo.'
        )
        return redirect('finanzas:editar_perfil')

    deudas = perfil.deudas.all()
    objetivos = perfil.objetivos.filter(activo=True)

    # Calculate financial summary
    total_deudas = deudas.aggregate(
        total=Sum('saldo_actual')
    )['total'] or Decimal('0.00')

    total_objetivos = objetivos.aggregate(
        total=Sum('monto_objetivo')
    )['total'] or Decimal('0.00')

    context: Dict[str, Any] = {
        'perfil': perfil,
        'deudas': deudas,
        'objetivos': objetivos,
        'total_deudas': total_deudas,
        'total_objetivos': total_objetivos,
    }
    return render(request, 'finanzas/perfil_financiero.html', context)


@login_required
def editar_perfil(request: HttpRequest) -> HttpResponse:
    """Vista para crear o editar el perfil financiero"""
    perfil = None
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
    except PerfilFinanciero.DoesNotExist:
        pass

    if request.method == 'POST':
        form = PerfilFinancieroForm(request.POST, instance=perfil)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.save()

            if perfil:
                messages.success(
                    request,
                    'Perfil financiero actualizado correctamente.'
                )
            else:
                messages.success(
                    request,
                    'Perfil financiero creado correctamente.'
                )

            return redirect('finanzas:perfil_financiero')
        else:
            messages.error(
                request,
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = PerfilFinancieroForm(instance=perfil)

    context: Dict[str, Any] = {
        'form': form,
        'perfil': perfil,
        'is_new': perfil is None,
    }
    return render(request, 'finanzas/editar_perfil.html', context)


@login_required
def lista_deudas(request: HttpRequest) -> HttpResponse:
    """Vista para listar las deudas del usuario"""
    deudas = []
    perfil = None

    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
        deudas = perfil.deudas.all().order_by('-saldo_actual')
    except PerfilFinanciero.DoesNotExist:
        messages.info(
            request,
            'Primero debes crear tu perfil financiero para gestionar deudas.'
        )

    # Calculate summary
    total_deudas = sum(deuda.saldo_actual for deuda in deudas)
    total_pagado = sum(deuda.pago_mensual for deuda in deudas)
    deudas_activas = sum(1 for deuda in deudas if deuda.activa)

    context: Dict[str, Any] = {
        'deudas': deudas,
        'perfil': perfil,
        'total_deudas': total_deudas,
        'total_pagado': total_pagado,
        'deudas_activas': deudas_activas,
    }
    return render(request, 'finanzas/lista_deudas.html', context)


@login_required
def nueva_deuda(request: HttpRequest) -> HttpResponse:
    """Vista para crear una nueva deuda"""
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
    except PerfilFinanciero.DoesNotExist:
        messages.error(
            request,
            'Primero debes crear tu perfil financiero.'
        )
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
            messages.error(
                request,
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = DeudaForm()

    context: Dict[str, Any] = {
        'form': form,
        'perfil': perfil,
    }
    return render(request, 'finanzas/nueva_deuda.html', context)


@login_required
def editar_deuda(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para editar una deuda existente"""
    deuda = get_object_or_404(
        Deuda,
        pk=pk,
        perfil__usuario=request.user
    )

    if request.method == 'POST':
        form = DeudaForm(request.POST, instance=deuda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deuda actualizada correctamente.')
            return redirect('finanzas:lista_deudas')
        else:
            messages.error(
                request,
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = DeudaForm(instance=deuda)

    context: Dict[str, Any] = {
        'form': form,
        'deuda': deuda,
    }
    return render(request, 'finanzas/editar_deuda.html', context)


@login_required
@require_POST
def eliminar_deuda(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para eliminar una deuda"""
    deuda = get_object_or_404(
        Deuda,
        pk=pk,
        perfil__usuario=request.user
    )
    nombre_deuda = deuda.nombre
    deuda.delete()
    messages.success(
        request,
        f'Deuda "{nombre_deuda}" eliminada correctamente.'
    )
    return redirect('finanzas:lista_deudas')


@login_required
def lista_objetivos(request: HttpRequest) -> HttpResponse:
    """Vista para listar los objetivos financieros del usuario"""
    objetivos = []
    perfil = None

    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
        objetivos = perfil.objetivos.all().order_by('-activo', 'fecha_limite')
    except PerfilFinanciero.DoesNotExist:
        messages.info(
            request,
            'Primero debes crear tu perfil financiero para gestionar objetivos.'
        )

    # Calculate progress
    objetivos_activos = [obj for obj in objetivos if obj.activo]
    objetivos_completados = [obj for obj in objetivos if obj.completado]

    context: Dict[str, Any] = {
        'objetivos': objetivos,
        'perfil': perfil,
        'objetivos_activos': len(objetivos_activos),
        'objetivos_completados': len(objetivos_completados),
    }
    return render(request, 'finanzas/lista_objetivos.html', context)


@login_required
def nuevo_objetivo(request: HttpRequest) -> HttpResponse:
    """Vista para crear un nuevo objetivo financiero"""
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
    except PerfilFinanciero.DoesNotExist:
        messages.error(
            request,
            'Debe completar su perfil financiero primero.'
        )
        return redirect('finanzas:editar_perfil')

    if request.method == 'POST':
        form = ObjetivoFinancieroForm(request.POST)
        if form.is_valid():
            objetivo = form.save(commit=False)
            objetivo.perfil = perfil
            objetivo.save()
            messages.success(
                request,
                'Objetivo financiero creado correctamente.'
            )
            return redirect('finanzas:lista_objetivos')
        else:
            messages.error(
                request,
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = ObjetivoFinancieroForm()

    context: Dict[str, Any] = {
        'form': form,
        'perfil': perfil,
    }
    return render(request, 'finanzas/nuevo_objetivo.html', context)


@login_required
def editar_objetivo(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para editar un objetivo financiero existente"""
    objetivo = get_object_or_404(
        ObjetivoFinanciero,
        pk=pk,
        perfil__usuario=request.user
    )

    if request.method == 'POST':
        form = ObjetivoFinancieroForm(request.POST, instance=objetivo)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Objetivo financiero actualizado correctamente.'
            )
            return redirect('finanzas:lista_objetivos')
        else:
            messages.error(
                request,
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = ObjetivoFinancieroForm(instance=objetivo)

    context: Dict[str, Any] = {
        'form': form,
        'objetivo': objetivo,
    }
    return render(request, 'finanzas/editar_objetivo.html', context)


@login_required
@require_POST
def eliminar_objetivo(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para eliminar un objetivo financiero"""
    objetivo = get_object_or_404(
        ObjetivoFinanciero,
        pk=pk,
        perfil__usuario=request.user
    )
    nombre_objetivo = objetivo.nombre
    objetivo.delete()
    messages.success(
        request,
        f'Objetivo "{nombre_objetivo}" eliminado correctamente.'
    )
    return redirect('finanzas:lista_objetivos')


@login_required
def lista_simulaciones(request: HttpRequest) -> HttpResponse:
    """Vista para listar las simulaciones de crédito del usuario"""
    simulaciones = []
    perfil = None

    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
        simulaciones = perfil.simulaciones.all().order_by('-fecha_simulacion')
    except PerfilFinanciero.DoesNotExist:
        messages.info(
            request,
            'Primero debes crear tu perfil financiero para realizar simulaciones.'
        )

    context: Dict[str, Any] = {
        'simulaciones': simulaciones,
        'perfil': perfil,
    }
    return render(request, 'finanzas/lista_simulaciones.html', context)


@login_required
def nueva_simulacion(request: HttpRequest) -> HttpResponse:
    """Vista para crear una nueva simulación de crédito"""
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
    except PerfilFinanciero.DoesNotExist:
        messages.error(
            request,
            'Primero debes crear tu perfil financiero.'
        )
        return redirect('finanzas:editar_perfil')

    if request.method == 'POST':
        form = SimulacionCreditoForm(request.POST)
        if form.is_valid():
            simulacion = form.save(commit=False)
            simulacion.perfil = perfil
            simulacion.save()
            messages.success(
                request,
                'Simulación de crédito creada correctamente.'
            )
            return redirect('finanzas:detalle_simulacion', pk=simulacion.pk)
        else:
            messages.error(
                request,
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = SimulacionCreditoForm()

    context: Dict[str, Any] = {
        'form': form,
        'perfil': perfil,
    }
    return render(request, 'finanzas/nueva_simulacion.html', context)


@login_required
def detalle_simulacion(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para mostrar los detalles de una simulación de crédito"""
    simulacion = get_object_or_404(
        SimulacionCredito,
        pk=pk,
        perfil__usuario=request.user
    )

    # Get amortization table
    tabla_amortizacion = []
    if hasattr(simulacion, 'tabla_amortizacion'):
        tabla_amortizacion = simulacion.tabla_amortizacion()[
            :12]  # First 12 months

    context: Dict[str, Any] = {
        'simulacion': simulacion,
        'tabla_amortizacion': tabla_amortizacion,
        'cuota_mensual': simulacion.pago_mensual,
        'total_intereses': simulacion.intereses_totales,
        'total_pagar': simulacion.pago_total,
    }
    return render(request, 'finanzas/detalle_simulacion.html', context)


@login_required
@require_POST
def eliminar_simulacion(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para eliminar una simulación de crédito"""
    simulacion = get_object_or_404(
        SimulacionCredito,
        pk=pk,
        perfil__usuario=request.user
    )
    simulacion.delete()
    messages.success(
        request,
        'Simulación de crédito eliminada correctamente.'
    )
    return redirect('finanzas:lista_simulaciones')


@login_required
def lista_recomendaciones(request: HttpRequest) -> HttpResponse:
    """Vista para listar las recomendaciones del usuario"""
    recomendaciones = []
    perfil = None

    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)
        recomendaciones = perfil.recomendaciones.filter(
            activa=True
        ).order_by('-prioridad', '-fecha_creacion')
    except PerfilFinanciero.DoesNotExist:
        messages.info(
            request,
            'Primero debes crear tu perfil financiero para recibir recomendaciones.'
        )

    # Group recommendations by type
    recomendaciones_por_tipo = {}
    for rec in recomendaciones:
        tipo = rec.tipo if hasattr(rec, 'tipo') else 'General'
        if tipo not in recomendaciones_por_tipo:
            recomendaciones_por_tipo[tipo] = []
        recomendaciones_por_tipo[tipo].append(rec)

    context: Dict[str, Any] = {
        'recomendaciones': recomendaciones,
        'recomendaciones_por_tipo': recomendaciones_por_tipo,
        'perfil': perfil,
    }
    return render(request, 'finanzas/lista_recomendaciones.html', context)


# AJAX endpoint for dashboard data
@login_required
def api_dashboard_summary(request: HttpRequest) -> JsonResponse:
    """API endpoint to get dashboard summary data"""
    try:
        perfil = PerfilFinanciero.objects.get(usuario=request.user)

        # Get financial summary
        deudas_total = perfil.deudas.filter(
            activa=True
        ).aggregate(
            total=Sum('saldo_actual')
        )['total'] or Decimal('0.00')

        objetivos_total = perfil.objetivos.filter(
            activo=True
        ).aggregate(
            total=Sum('monto_objetivo')
        )['total'] or Decimal('0.00')

        data = {
            'success': True,
            'perfil_exists': True,
            'summary': {
                'ingresos_mensuales': float(perfil.ingreso_mensual),
                'gastos_mensuales': float(perfil.gastos_fijos),
                'deudas_total': float(deudas_total),
                'objetivos_total': float(objetivos_total),
                'ahorro_disponible': float(
                    perfil.ingreso_mensual - perfil.gastos_fijos
                ),
            }
        }
    except PerfilFinanciero.DoesNotExist:
        data = {
            'success': True,
            'perfil_exists': False,
            'message': 'No financial profile found'
        }
    except Exception as e:
        data = {
            'success': False,
            'error': str(e)
        }

    return JsonResponse(data)


# ============================================================================
# NEW FINANCIAL MODELS VIEWS
# ============================================================================

@login_required
def account_list(request: HttpRequest) -> HttpResponse:
    """Vista para listar las cuentas del usuario"""
    accounts = Account.objects.filter(user=request.user, is_active=True)

    # Calculate summary
    total_balance = accounts.aggregate(
        total=Sum('current_balance')
    )['total'] or Decimal('0.00')

    # Group by account type
    accounts_by_type = {}
    for account in accounts:
        account_type = account.get_account_type_display()
        if account_type not in accounts_by_type:
            accounts_by_type[account_type] = []
        accounts_by_type[account_type].append(account)

    context: Dict[str, Any] = {
        'accounts': accounts,
        'accounts_by_type': accounts_by_type,
        'total_balance': total_balance,
        'account_count': len(accounts),
    }
    return render(request, 'finanzas/account_list.html', context)


@login_required
def account_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para mostrar los detalles de una cuenta"""
    account = get_object_or_404(Account, pk=pk, user=request.user)

    # Get recent transactions
    recent_transactions = account.transactions.filter(
        is_cancelled=False
    ).select_related('category').order_by('-date', '-created_at')[:20]

    # Get transaction summary
    income = account.transactions.filter(
        transaction_type=Transaction.TransactionType.INCOME,
        is_cancelled=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    expenses = account.transactions.filter(
        transaction_type=Transaction.TransactionType.EXPENSE,
        is_cancelled=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    transfers_out = account.transactions.filter(
        transaction_type=Transaction.TransactionType.TRANSFER,
        is_cancelled=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    transfers_in = account.incoming_transfers.filter(
        is_cancelled=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context: Dict[str, Any] = {
        'account': account,
        'recent_transactions': recent_transactions,
        'income': income,
        'expenses': expenses,
        'transfers_out': transfers_out,
        'transfers_in': transfers_in,
        'net_flow': income - expenses - transfers_out + transfers_in,
    }
    return render(request, 'finanzas/account_detail.html', context)


@login_required
def account_create(request: HttpRequest) -> HttpResponse:
    """Vista para crear una nueva cuenta"""
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        account_type = request.POST.get('account_type')
        currency = request.POST.get('currency')
        initial_balance = request.POST.get('initial_balance', '0.00')
        description = request.POST.get('description', '')

        if name and account_type and currency:
            try:
                account = Account.objects.create(
                    user=request.user,
                    name=name,
                    account_type=account_type,
                    currency=currency,
                    initial_balance=Decimal(initial_balance),
                    current_balance=Decimal(initial_balance),
                    description=description
                )
                messages.success(
                    request, f'Cuenta "{name}" creada correctamente.')
                return redirect('finanzas:account_detail', pk=account.pk)
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
        else:
            messages.error(
                request, 'Por favor, completa todos los campos requeridos.')

    context: Dict[str, Any] = {
        'account_types': Account.AccountType.choices,
        'currencies': Account.Currency.choices,
    }
    return render(request, 'finanzas/account_form.html', context)


@login_required
def account_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para actualizar una cuenta"""
    account = get_object_or_404(Account, pk=pk, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        account_type = request.POST.get('account_type')
        currency = request.POST.get('currency')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        if name and account_type and currency:
            try:
                account.name = name
                account.account_type = account_type
                account.currency = currency
                account.description = description
                account.is_active = is_active
                account.save()
                messages.success(
                    request, f'Cuenta "{name}" actualizada correctamente.')
                return redirect('finanzas:account_detail', pk=account.pk)
            except Exception as e:
                messages.error(
                    request, f'Error al actualizar la cuenta: {str(e)}')
        else:
            messages.error(
                request, 'Por favor, completa todos los campos requeridos.')

    context: Dict[str, Any] = {
        'account': account,
        'account_types': Account.AccountType.choices,
        'currencies': Account.Currency.choices,
    }
    return render(request, 'finanzas/account_form.html', context)


@login_required
@require_POST
def account_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para eliminar una cuenta"""
    account = get_object_or_404(Account, pk=pk, user=request.user)
    name = account.name

    # Check if account has transactions
    if account.transactions.exists():
        messages.error(
            request,
            f'No se puede eliminar la cuenta "{name}" porque tiene transacciones asociadas.'
        )
        return redirect('finanzas:account_detail', pk=account.pk)

    account.delete()
    messages.success(request, f'Cuenta "{name}" eliminada correctamente.')
    return redirect('finanzas:account_list')


@login_required
def transaction_list(request: HttpRequest) -> HttpResponse:
    """Vista para listar las transacciones del usuario"""
    transactions = Transaction.objects.filter(
        user=request.user,
        is_cancelled=False
    ).select_related('account', 'category').order_by('-date', '-created_at')

    # Apply filters
    account_id = request.GET.get('account')
    category_id = request.GET.get('category')
    transaction_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if account_id:
        transactions = transactions.filter(account_id=account_id)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    accounts = Account.objects.filter(user=request.user, is_active=True)
    categories = Category.objects.all()

    # Calculate summary
    total_income = transactions.filter(
        transaction_type=Transaction.TransactionType.INCOME
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    total_expenses = transactions.filter(
        transaction_type=Transaction.TransactionType.EXPENSE
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    total_transfers = transactions.filter(
        transaction_type=Transaction.TransactionType.TRANSFER
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context: Dict[str, Any] = {
        'page_obj': page_obj,
        'accounts': accounts,
        'categories': categories,
        'transaction_types': Transaction.TransactionType.choices,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_transfers': total_transfers,
        'net_flow': total_income - total_expenses,
        'filters': {
            'account_id': account_id,
            'category_id': category_id,
            'transaction_type': transaction_type,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    return render(request, 'finanzas/transaction_list.html', context)


@login_required
def transaction_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para mostrar los detalles de una transacción"""
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )

    context: Dict[str, Any] = {
        'transaction': transaction,
    }
    return render(request, 'finanzas/transaction_detail.html', context)


@login_required
def transaction_create(request: HttpRequest) -> HttpResponse:
    """Vista para crear una nueva transacción"""
    if request.method == 'POST':
        # Handle form submission
        account_id = request.POST.get('account')
        transaction_type = request.POST.get('transaction_type')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date')
        notes = request.POST.get('notes', '')
        is_recurring = request.POST.get('is_recurring') == 'on'

        if all([account_id, transaction_type, amount, description, date]):
            try:
                account = Account.objects.get(id=account_id, user=request.user)
                category = None
                if category_id:
                    category = Category.objects.get(id=category_id)

                transaction = Transaction.objects.create(
                    user=request.user,
                    account=account,
                    transaction_type=transaction_type,
                    category=category,
                    amount=Decimal(amount),
                    description=description,
                    date=date,
                    notes=notes,
                    is_recurring=is_recurring
                )
                messages.success(request, 'Transacción creada correctamente.')
                return redirect('finanzas:transaction_detail', pk=transaction.pk)
            except Exception as e:
                messages.error(
                    request, f'Error al crear la transacción: {str(e)}')
        else:
            messages.error(
                request, 'Por favor, completa todos los campos requeridos.')

    context: Dict[str, Any] = {
        'accounts': Account.objects.filter(user=request.user, is_active=True),
        'categories': Category.objects.all(),
        'transaction_types': Transaction.TransactionType.choices,
    }
    return render(request, 'finanzas/transaction_form.html', context)


@login_required
def transaction_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para actualizar una transacción"""
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':
        account_id = request.POST.get('account')
        transaction_type = request.POST.get('transaction_type')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date')
        notes = request.POST.get('notes', '')
        is_recurring = request.POST.get('is_recurring') == 'on'

        if all([account_id, transaction_type, amount, description, date]):
            try:
                account = Account.objects.get(id=account_id, user=request.user)
                category = None
                if category_id:
                    category = Category.objects.get(id=category_id)

                transaction.account = account
                transaction.transaction_type = transaction_type
                transaction.category = category
                transaction.amount = Decimal(amount)
                transaction.description = description
                transaction.date = date
                transaction.notes = notes
                transaction.is_recurring = is_recurring
                transaction.save()

                messages.success(
                    request, 'Transacción actualizada correctamente.')
                return redirect('finanzas:transaction_detail', pk=transaction.pk)
            except Exception as e:
                messages.error(
                    request, f'Error al actualizar la transacción: {str(e)}')
        else:
            messages.error(
                request, 'Por favor, completa todos los campos requeridos.')

    context: Dict[str, Any] = {
        'transaction': transaction,
        'accounts': Account.objects.filter(user=request.user, is_active=True),
        'categories': Category.objects.all(),
        'transaction_types': Transaction.TransactionType.choices,
    }
    return render(request, 'finanzas/transaction_form.html', context)


@login_required
@require_POST
def transaction_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para eliminar una transacción"""
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )

    # Instead of deleting, mark as cancelled
    transaction.is_cancelled = True
    transaction.save()

    messages.success(request, 'Transacción cancelada correctamente.')
    return redirect('finanzas:transaction_list')


@login_required
def budget_list(request: HttpRequest) -> HttpResponse:
    """Vista para listar los presupuestos del usuario"""
    budgets = Budget.objects.filter(user=request.user).order_by('-start_date')

    # Get active budgets
    active_budgets = budgets.filter(is_active=True)

    # Calculate summary
    total_budgeted = active_budgets.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')

    total_spent = sum(budget.spent_amount for budget in active_budgets)
    total_remaining = total_budgeted - total_spent

    context: Dict[str, Any] = {
        'budgets': budgets,
        'active_budgets': active_budgets,
        'total_budgeted': total_budgeted,
        'total_spent': total_spent,
        'total_remaining': total_remaining,
        'budget_periods': Budget.BudgetPeriod.choices,
    }
    return render(request, 'finanzas/budget_list.html', context)


@login_required
def budget_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Vista para mostrar los detalles de un presupuesto"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    # Get budget categories
    budget_categories = budget.categories.all().select_related('category')

    # Get transactions in budget period
    transactions = Transaction.objects.filter(
        user=request.user,
        date__range=[budget.start_date, budget.end_date],
        transaction_type=Transaction.TransactionType.EXPENSE,
        is_cancelled=False
    ).select_related('category')

    context: Dict[str, Any] = {
        'budget': budget,
        'budget_categories': budget_categories,
        'transactions': transactions,
    }
    return render(request, 'finanzas/budget_detail.html', context)


@login_required
def category_list(request: HttpRequest) -> HttpResponse:
    """Vista para listar las categorías"""
    categories = Category.objects.all().order_by('name')

    # Group by parent
    parent_categories = categories.filter(parent=None)
    subcategories = categories.filter(parent__isnull=False)

    context: Dict[str, Any] = {
        'parent_categories': parent_categories,
        'subcategories': subcategories,
        'categories': categories,
    }
    return render(request, 'finanzas/category_list.html', context)
