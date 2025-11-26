from django.contrib import admin
from core.models import Empresa, CategoriaTransaccion, MetodoPago


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """Administración de Empresas."""
    list_display = ['id', 'nombre', 'ruc', 'regimen_tributario']
    search_fields = ['nombre', 'ruc']
    list_filter = ['regimen_tributario']


@admin.register(CategoriaTransaccion)
class CategoriaTransaccionAdmin(admin.ModelAdmin):
    """Administración de Categorías de Transacción."""
    list_display = ['id', 'nombre', 'tipo']
    list_filter = ['tipo']
    search_fields = ['nombre']
    ordering = ['tipo', 'nombre']


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    """Administración de Métodos de Pago."""
    list_display = ['id', 'nombre']
    search_fields = ['nombre']
    ordering = ['nombre']

