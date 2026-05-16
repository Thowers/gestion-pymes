from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum

from .models import Cliente, Deuda, Abono
from .forms import ClienteForm, AbonoForm


@login_required
def lista_clientes(request):
    query = request.GET.get('q', '')
    solo_deudores = request.GET.get('deudores', '')

    clientes = Cliente.objects.filter(activo=True)
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) | Q(documento__icontains=query)
        )

    # Anotamos el saldo total por cliente
    clientes = clientes.annotate(
        saldo_anotado=Sum('deudas__saldo', filter=Q(deudas__activa=True))
    )
    if solo_deudores:
        clientes = clientes.filter(saldo_anotado__gt=0)

    return render(request, 'cartera/lista_clientes.html', {
        'clientes': clientes,
        'query': query,
        'solo_deudores': solo_deudores,
    })


@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente "{cliente.nombre}" registrado.')
            return redirect('detalle_cliente', pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, 'cartera/formulario_cliente.html', {'form': form, 'titulo': 'Nuevo Cliente'})


@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado.')
            return redirect('detalle_cliente', pk=pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'cartera/formulario_cliente.html', {
        'form': form, 'titulo': 'Editar Cliente', 'cliente': cliente
    })


@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    deudas = cliente.deudas.filter(activa=True).prefetch_related('abonos')
    historial_abonos = Abono.objects.filter(
        deuda__cliente=cliente
    ).select_related('usuario', 'deuda').order_by('-fecha')[:20]

    return render(request, 'cartera/detalle_cliente.html', {
        'cliente': cliente,
        'deudas': deudas,
        'historial_abonos': historial_abonos,
    })


@login_required
def registrar_abono(request, deuda_pk):
    deuda = get_object_or_404(Deuda, pk=deuda_pk, activa=True)

    if request.method == 'POST':
        form = AbonoForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']

            if monto > deuda.saldo:
                messages.error(request, f'El abono (${monto}) supera el saldo pendiente (${deuda.saldo}).')
                return redirect('registrar_abono', deuda_pk=deuda_pk)

            with transaction.atomic():
                abono = form.save(commit=False)
                abono.deuda = deuda
                abono.usuario = request.user
                abono.save()

                # Actualizar saldo de la deuda
                deuda.saldo -= monto
                if deuda.saldo <= 0:
                    deuda.saldo = 0
                    deuda.activa = False
                deuda.save()

            messages.success(
                request,
                f'✅ Abono registrado. Comprobante: {abono.comprobante}. '
                f'Saldo pendiente: ${deuda.saldo}'
            )
            return redirect('detalle_cliente', pk=deuda.cliente.pk)
    else:
        form = AbonoForm()

    return render(request, 'cartera/registrar_abono.html', {
        'form': form, 'deuda': deuda
    })
