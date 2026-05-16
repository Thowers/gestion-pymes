from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse

from .models import Producto, Categoria, MovimientoStock
from .forms import ProductoForm, CategoriaForm, MovimientoStockForm


@login_required
def lista_productos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    solo_bajos = request.GET.get('bajos', '')

    productos = Producto.objects.select_related('categoria').filter(activo=True)

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query)
        )
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Filtro de stock bajo: stock_actual <= stock_minimo
    if solo_bajos:
        from django.db.models import F
        productos = productos.filter(stock_actual__lte=F('stock_minimo'))

    categorias = Categoria.objects.all()
    context = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
        'solo_bajos': solo_bajos,
    }
    return render(request, 'inventario/lista_productos.html', context)


@login_required
def crear_producto(request):
    if not request.user.es_admin():
        messages.error(request, 'Solo los administradores pueden crear productos.')
        return redirect('lista_productos')

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            # Registrar movimiento inicial si tiene stock
            if producto.stock_actual > 0:
                MovimientoStock.objects.create(
                    producto=producto,
                    tipo='entrada',
                    cantidad=producto.stock_actual,
                    stock_anterior=0,
                    stock_nuevo=producto.stock_actual,
                    motivo='Stock inicial al crear producto',
                    usuario=request.user,
                )
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm()

    return render(request, 'inventario/formulario_producto.html', {'form': form, 'titulo': 'Nuevo Producto'})


@login_required
def editar_producto(request, pk):
    if not request.user.es_admin():
        messages.error(request, 'Solo los administradores pueden editar productos.')
        return redirect('lista_productos')

    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado.')
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inventario/formulario_producto.html', {
        'form': form, 'titulo': 'Editar Producto', 'producto': producto
    })


@login_required
def eliminar_producto(request, pk):
    if not request.user.es_admin():
        messages.error(request, 'Solo los administradores pueden eliminar productos.')
        return redirect('lista_productos')

    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.activo = False
        producto.save()
        messages.success(request, f'Producto "{producto.nombre}" desactivado.')
        return redirect('lista_productos')

    return render(request, 'inventario/confirmar_eliminar.html', {'producto': producto})


@login_required
def registrar_movimiento(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                stock_anterior = producto.stock_actual
                tipo = form.cleaned_data['tipo']
                cantidad = form.cleaned_data['cantidad']

                if tipo == 'entrada':
                    producto.stock_actual += cantidad
                elif tipo == 'salida':
                    if cantidad > producto.stock_actual:
                        messages.error(request, 'No hay suficiente stock para hacer la salida.')
                        return redirect('registrar_movimiento', pk=pk)
                    producto.stock_actual -= cantidad
                elif tipo == 'ajuste':
                    producto.stock_actual = cantidad  # ajuste directo al valor

                producto.save()
                MovimientoStock.objects.create(
                    producto=producto,
                    tipo=tipo,
                    cantidad=cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=producto.stock_actual,
                    motivo=form.cleaned_data.get('motivo', ''),
                    usuario=request.user,
                )
            messages.success(request, f'Movimiento registrado. Stock actual: {producto.stock_actual}')
            return redirect('lista_productos')
    else:
        form = MovimientoStockForm()

    return render(request, 'inventario/movimiento_stock.html', {
        'form': form, 'producto': producto
    })


@login_required
def historial_movimientos(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    movimientos = producto.movimientos.select_related('usuario').all()
    return render(request, 'inventario/historial_movimientos.html', {
        'producto': producto, 'movimientos': movimientos
    })


@login_required
def lista_categorias(request):
    categorias = Categoria.objects.all()
    form = CategoriaForm()
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada.')
            return redirect('lista_categorias')
    return render(request, 'inventario/lista_categorias.html', {
        'categorias': categorias, 'form': form
    })


# ── AJAX: buscar producto por código o nombre ──────────────────────────────────
def buscar_producto_ajax(request):
    """Endpoint AJAX para el POS: busca productos por código o nombre."""
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse({'productos': []})

    productos = Producto.objects.filter(
        Q(nombre__icontains=q) | Q(codigo__icontains=q),
        activo=True,
        stock_actual__gt=0,
    ).values('id', 'codigo', 'nombre', 'precio_venta', 'stock_actual')[:10]

    return JsonResponse({'productos': list(productos)})
