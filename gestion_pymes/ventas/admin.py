from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'fecha', 'cliente', 'tipo_pago', 'total', 'usuario')
    list_filter = ('tipo_pago', 'fecha')
    inlines = [DetalleInline]
    readonly_fields = ('fecha', 'total')
