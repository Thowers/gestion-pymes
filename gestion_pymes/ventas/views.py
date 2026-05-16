import json
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone

from .models import Venta, DetalleVenta
from inventario.models import Producto, MovimientoStock
from cartera.models import Cliente, Deuda


@login_required
def pos(request):
    """Vista principal del punto de venta."""
    clientes = Cliente.objects.filter(activo=True).order_by('nombre')
    return render(request, 'ventas/pos.html', {'clientes': clientes})


@require_POST
@login_required
def procesar_venta(request):
    """
    Procesa la venta completa de forma atómica (ACID).
    Recibe JSON con los items del carrito.
    """
    print(">>> PETICIÓN RECIBIDA")   # ← agrega esta línea temporal
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        tipo_pago = data.get('tipo_pago', 'efectivo')
        cliente_id = data.get('cliente_id')
        observaciones = data.get('observaciones', '')

        if not items:
            return JsonResponse({'ok': False, 'error': 'El carrito está vacío.'})

        with transaction.atomic():
            # 1. Obtener cliente (opcional)
            cliente = None
            if cliente_id:
                cliente = get_object_or_404(Cliente, pk=cliente_id)

            # 2. Validar y calcular total
            total = Decimal('0')
            productos_dict = {}
            for item in items:
                producto = Producto.objects.get(pk=item['producto_id'])
                cantidad = int(item['cantidad'])

                if cantidad <= 0:
                    raise ValueError(f"Cantidad inválida para {producto.nombre}")
                if producto.stock_actual < cantidad:
                    raise ValueError(
                        f"Stock insuficiente para '{producto.nombre}'. "
                        f"Disponible: {producto.stock_actual}"
                    )

                subtotal = producto.precio_venta * cantidad
                total += subtotal
                productos_dict[producto.pk] = {
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio_unitario': producto.precio_venta,
                    'subtotal': subtotal,
                }

            # 3. Crear la venta
            venta = Venta.objects.create(
                usuario=request.user,
                cliente=cliente,
                tipo_pago=tipo_pago,
                total=total,
                observaciones=observaciones,
            )

            # 4. Crear detalles y descontar stock
            for info in productos_dict.values():
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=info['producto'],
                    cantidad=info['cantidad'],
                    precio_unitario=info['precio_unitario'],
                    subtotal=info['subtotal'],
                )
                stock_anterior = info['producto'].stock_actual
                info['producto'].stock_actual -= info['cantidad']
                info['producto'].save()

                # Registrar movimiento de stock (auditoría)
                MovimientoStock.objects.create(
                    producto=info['producto'],
                    tipo='salida',
                    cantidad=info['cantidad'],
                    stock_anterior=stock_anterior,
                    stock_nuevo=info['producto'].stock_actual,
                    motivo=f'Venta #{venta.pk}',
                    usuario=request.user,
                )

            # 5. Si es crédito, crear la deuda
            if tipo_pago == 'credito':
                if not cliente:
                    raise ValueError("Para ventas a crédito se requiere seleccionar un cliente.")
                Deuda.objects.create(
                    cliente=cliente,
                    venta=venta,
                    monto_total=total,
                    saldo=total,
                )

        return JsonResponse({
            'ok': True,
            'venta_id': venta.pk,
            'numero': venta.numero_formateado,
            'total': str(total),
        })

    except Producto.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Producto no encontrado.'})
    except ValueError as e:
        return JsonResponse({'ok': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'Error inesperado: {str(e)}'})


@login_required
def historial_ventas(request):
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')

    ventas = Venta.objects.select_related('usuario', 'cliente').prefetch_related('detalles')

    if fecha_desde:
        ventas = ventas.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha__date__lte=fecha_hasta)

    ventas = ventas[:100]  # límite para evitar cargar demasiado

    return render(request, 'ventas/historial.html', {
        'ventas': ventas,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })


@login_required
def detalle_venta(request, pk):
    venta = get_object_or_404(
        Venta.objects.select_related('usuario', 'cliente').prefetch_related('detalles__producto'),
        pk=pk
    )
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})
