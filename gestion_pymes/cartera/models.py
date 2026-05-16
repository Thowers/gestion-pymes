from django.db import models
from django.db.models import Sum
import uuid


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    documento = models.CharField(max_length=20, blank=True, verbose_name='Documento (CC/NIT)')
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def saldo_total(self):
        total = self.deudas.filter(activa=True).aggregate(s=Sum('saldo'))['s']
        return total or 0

    @property
    def tiene_deudas(self):
        return self.saldo_total > 0


class Deuda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='deudas')
    venta = models.OneToOneField(
        'ventas.Venta', on_delete=models.CASCADE, null=True, blank=True, related_name='deuda'
    )
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto total')
    saldo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Saldo pendiente')
    fecha = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Deuda'
        verbose_name_plural = 'Deudas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Deuda {self.pk} - {self.cliente.nombre} (${self.saldo})"

    def esta_saldada(self):
        return self.saldo <= 0


class Abono(models.Model):
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='abonos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        'core.Usuario', on_delete=models.SET_NULL, null=True, related_name='abonos'
    )
    # Comprobante único generado automáticamente
    comprobante = models.CharField(max_length=20, unique=True, editable=False)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Abono'
        verbose_name_plural = 'Abonos'
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        if not self.comprobante:
            # Genera un código único tipo: AB-2024-0001A
            from django.utils import timezone
            year = timezone.now().year
            short_id = str(uuid.uuid4()).upper()[:6]
            self.comprobante = f"AB-{year}-{short_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Abono {self.comprobante} - ${self.monto}"
