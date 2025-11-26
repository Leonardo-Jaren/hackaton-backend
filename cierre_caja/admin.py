from django.contrib import admin
from cierre_caja.models import CierreCaja, ResumenEfectivo, ResumenMetodoPago, ResultadoCuadre


class ResumenEfectivoInline(admin.TabularInline):
    """Inline para mostrar el resumen de efectivo en el detalle del cierre."""
    model = ResumenEfectivo
    extra = 0
    readonly_fields = ['efectivo_contado_fisico', 'ventas_efectivo_sistema', 'diferencia_efectivo']


class ResumenMetodoPagoInline(admin.TabularInline):
    """Inline para mostrar los resúmenes de métodos de pago."""
    model = ResumenMetodoPago
    extra = 0
    readonly_fields = ['metodo_pago', 'monto_sistema', 'monto_banco_o_pos', 'diferencia']


class ResultadoCuadreInline(admin.StackedInline):
    """Inline para mostrar el resultado del cuadre."""
    model = ResultadoCuadre
    extra = 0
    readonly_fields = ['es_encuadre_perfecto', 'faltante_total', 'sobrante_total', 'observaciones']


@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    """Administración de Cierres de Caja."""
    list_display = ['id', 'fecha_cierre', 'cajero', 'empresa', 'estado', 'get_fondo_inicial']
    list_filter = ['estado', 'fecha_cierre', 'empresa']
    search_fields = ['cajero__email', 'empresa__nombre']
    readonly_fields = ['fecha_cierre']
    inlines = [ResumenEfectivoInline, ResumenMetodoPagoInline, ResultadoCuadreInline]
    
    def get_fondo_inicial(self, obj):
        """Muestra el monto del fondo inicial."""
        return f"${obj.fondo_inicial.monto_inicial}"
    get_fondo_inicial.short_description = 'Fondo Inicial'


@admin.register(ResumenEfectivo)
class ResumenEfectivoAdmin(admin.ModelAdmin):
    """Administración de Resúmenes de Efectivo."""
    list_display = ['id', 'cierre', 'efectivo_contado_fisico', 'ventas_efectivo_sistema', 'diferencia_efectivo']
    list_filter = ['cierre__estado']
    search_fields = ['cierre__id', 'cierre__cajero__email']


@admin.register(ResumenMetodoPago)
class ResumenMetodoPagoAdmin(admin.ModelAdmin):
    """Administración de Resúmenes de Métodos de Pago."""
    list_display = ['id', 'cierre', 'metodo_pago', 'monto_sistema', 'monto_banco_o_pos', 'diferencia']
    list_filter = ['metodo_pago', 'cierre__estado']
    search_fields = ['cierre__id', 'metodo_pago__nombre']


@admin.register(ResultadoCuadre)
class ResultadoCuadreAdmin(admin.ModelAdmin):
    """Administración de Resultados de Cuadre."""
    list_display = ['id', 'cierre', 'es_encuadre_perfecto', 'faltante_total', 'sobrante_total']
    list_filter = ['es_encuadre_perfecto', 'cierre__estado']
    search_fields = ['cierre__id', 'observaciones']
    readonly_fields = ['es_encuadre_perfecto', 'faltante_total', 'sobrante_total']

