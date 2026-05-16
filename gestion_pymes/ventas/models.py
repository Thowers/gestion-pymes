from django.db import models


class Venta(models.Model):
    PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('credito', 'Crédito'),
        ('transferencia', 'Transferencia'),
        ('mixto', 'Mixto'),
    ]
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        'core.Usuario', on_delete=models.SET_NULL, null=True, related_name='ventas'
    )
    cliente = models.ForeignKey(
        'cartera.Cliente', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas'
    )
    tipo_pago = models.CharField(max_length=15, choices=PAGO_CHOICES, default='efectivo')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha.strftime('%d/%m/%Y')} - ${self.total}"

    @property
    def numero_formateado(self):
        return f"V-{self.pk:06d}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(
        'inventario.Producto', on_delete=models.PROTECT, related_name='detalles_venta'
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
