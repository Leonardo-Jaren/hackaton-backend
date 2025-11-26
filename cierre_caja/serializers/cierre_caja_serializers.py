from rest_framework import serializers
from cierre_caja.serializers.base import BaseModelSerializer
from cierre_caja.models import CierreCaja, ResumenEfectivo, ResumenMetodoPago, ResultadoCuadre
from decimal import Decimal


# --- Serializers de Entrada ---

class IniciarCierreSerializer(serializers.Serializer):
    """Serializer para iniciar un nuevo cierre de caja."""
    fondo_caja_id = serializers.IntegerField(required=True, help_text="ID del FondoCaja utilizado")


class RegistrarEfectivoSerializer(serializers.Serializer):
    """Serializer para registrar el conteo físico de efectivo."""
    efectivo_contado_fisico = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True,
        help_text="Monto de efectivo contado físicamente en la caja"
    )

    def validate_efectivo_contado_fisico(self, value):
        """Valida que el monto sea positivo o cero."""
        if value < 0:
            raise serializers.ValidationError("El monto de efectivo no puede ser negativo.")
        return value


class FinalizarCierreSerializer(serializers.Serializer):
    """Serializer para finalizar el cierre de caja."""
    observaciones = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Observaciones adicionales sobre el cierre"
    )


# --- Serializers de Salida ---

class ResumenEfectivoSerializer(BaseModelSerializer):
    """Serializer para mostrar el resumen de efectivo."""
    
    class Meta:
        model = ResumenEfectivo
        fields = [
            'id',
            'efectivo_contado_fisico',
            'ventas_efectivo_sistema',
            'diferencia_efectivo'
        ]


class ResumenMetodoPagoSerializer(BaseModelSerializer):
    """Serializer para mostrar el resumen por método de pago."""
    metodo_pago_nombre = serializers.CharField(source='metodo_pago.nombre', read_only=True)
    
    class Meta:
        model = ResumenMetodoPago
        fields = [
            'id',
            'metodo_pago',
            'metodo_pago_nombre',
            'monto_sistema',
            'monto_banco_o_pos',
            'diferencia'
        ]


class ResultadoCuadreSerializer(BaseModelSerializer):
    """Serializer para mostrar el resultado del cuadre."""
    
    class Meta:
        model = ResultadoCuadre
        fields = [
            'id',
            'es_encuadre_perfecto',
            'faltante_total',
            'sobrante_total',
            'observaciones'
        ]


class CierreCajaDetalleSerializer(BaseModelSerializer):
    """Serializer completo para mostrar el detalle de un cierre de caja."""
    cajero_email = serializers.CharField(source='cajero.email', read_only=True)
    cajero_nombre = serializers.SerializerMethodField()
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    fondo_inicial_monto = serializers.DecimalField(
        source='fondo_inicial.monto_inicial',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    resumenes_efectivo = ResumenEfectivoSerializer(many=True, read_only=True)
    resumenes_metodo_pago = ResumenMetodoPagoSerializer(many=True, read_only=True)
    resultados_cuadre = ResultadoCuadreSerializer(many=True, read_only=True)
    
    class Meta:
        model = CierreCaja
        fields = [
            'id',
            'fecha_cierre',
            'cajero',
            'cajero_email',
            'cajero_nombre',
            'empresa',
            'empresa_nombre',
            'fondo_inicial',
            'fondo_inicial_monto',
            'estado',
            'resumenes_efectivo',
            'resumenes_metodo_pago',
            'resultados_cuadre'
        ]

    def get_cajero_nombre(self, obj):
        """Obtiene el nombre completo del cajero."""
        return obj.cajero.get_full_name() or obj.cajero.email


class CierreCajaListSerializer(BaseModelSerializer):
    """Serializer simplificado para listar cierres de caja."""
    cajero_email = serializers.CharField(source='cajero.email', read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = CierreCaja
        fields = [
            'id',
            'fecha_cierre',
            'cajero_email',
            'empresa_nombre',
            'estado'
        ]


class ResumenCierreSerializer(serializers.Serializer):
    """Serializer para mostrar el resumen esperado del cierre (antes del conteo físico)."""
    cierre_id = serializers.IntegerField()
    estado = serializers.CharField()
    fondo_inicial = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Totales por tipo de transacción
    total_ingresos = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_egresos = serializers.DecimalField(max_digits=10, decimal_places=2)
    saldo_esperado = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Detalle por método de pago
    ventas_efectivo = serializers.DecimalField(max_digits=10, decimal_places=2)
    metodos_pago = serializers.ListField(child=serializers.DictField())
