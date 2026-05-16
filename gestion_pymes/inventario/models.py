from django.db import models
from django.db.models import F


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='productos'
    )
    descripcion = models.TextField(blank=True)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio de venta')
    precio_costo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio de costo')
    stock_actual = models.IntegerField(default=0, verbose_name='Stock actual')
    stock_minimo = models.IntegerField(default=5, verbose_name='Stock mínimo')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

    @property
    def margen(self):
        if self.precio_costo and self.precio_costo > 0:
            return round(((self.precio_venta - self.precio_costo) / self.precio_costo) * 100, 1)
        return 0


class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada de stock'),
        ('salida', 'Salida manual'),
        ('ajuste', 'Ajuste de inventario'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    stock_anterior = models.IntegerField(default=0)
    stock_nuevo = models.IntegerField(default=0)
    motivo = models.CharField(max_length=300, blank=True)
    usuario = models.ForeignKey(
        'core.Usuario', on_delete=models.SET_NULL, null=True, related_name='movimientos'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de stock'
        verbose_name_plural = 'Movimientos de stock'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})"
