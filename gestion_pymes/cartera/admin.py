from django.contrib import admin
from .models import Cliente, Deuda, Abono

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'documento', 'telefono', 'activo')
    search_fields = ('nombre', 'documento')

@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'monto_total', 'saldo', 'fecha', 'activa')
    list_filter = ('activa',)

@admin.register(Abono)
class AbonoAdmin(admin.ModelAdmin):
    list_display = ('comprobante', 'deuda', 'monto', 'fecha', 'usuario')
    readonly_fields = ('comprobante', 'fecha')
