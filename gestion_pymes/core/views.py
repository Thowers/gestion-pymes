from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
import json

from inventario.models import Producto
from ventas.models import Venta, DetalleVenta
from cartera.models import Cliente, Deuda


@login_required
def dashboard(request):
    hoy = timezone.localdate()

    # --- Métricas del día ---
    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    total_hoy = ventas_hoy.aggregate(t=Sum('total'))['t'] or 0
    num_ventas_hoy = ventas_hoy.count()

    # --- Alertas de stock ---
    productos_bajos = Producto.objects.filter(
        activo=True, stock_actual__lte=models_stock_minimo()
    ).count()

    # --- Clientes con saldo pendiente ---
    clientes_deuda = Deuda.objects.filter(saldo__gt=0).values('cliente').distinct().count()

    # --- Últimas 10 ventas ---
    ultimas_ventas = Venta.objects.select_related('usuario', 'cliente').order_by('-fecha')[:10]

    # --- Gráfico: ventas últimos 7 días ---
    labels = []
    datos_ventas = []
    for i in range(6, -1, -1):
        dia = hoy - timezone.timedelta(days=i)
        total = Venta.objects.filter(fecha__date=dia).aggregate(t=Sum('total'))['t'] or 0
        labels.append(dia.strftime('%d/%m'))
        datos_ventas.append(float(total))

    # --- Productos más vendidos (top 5) ---
    top_productos = (
        DetalleVenta.objects
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    context = {
        'total_hoy': total_hoy,
        'num_ventas_hoy': num_ventas_hoy,
        'productos_bajos': productos_bajos,
        'clientes_deuda': clientes_deuda,
        'ultimas_ventas': ultimas_ventas,
        'grafico_labels': json.dumps(labels),
        'grafico_datos': json.dumps(datos_ventas),
        'top_productos': list(top_productos),
    }
    return render(request, 'core/dashboard.html', context)


def models_stock_minimo():
    """Helper: devuelve referencia al campo para el filtro dinámico."""
    from django.db.models import F
    return F('stock_minimo')
