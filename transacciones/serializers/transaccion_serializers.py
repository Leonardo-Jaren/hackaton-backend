from rest_framework import serializers
from ..models import (
    Transaccion, Empresa, CategoriaTransaccion, MetodoPago,
    FondoCaja, ArchivoIA, ResultadoIA
)

# Serializers básicos
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'


class CategoriaTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaTransaccion
        fields = '__all__'


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'


# Fondo de Caja
class FondoCajaSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    
    class Meta:
        model = FondoCaja
        fields = [
            'id', 'empresa', 'empresa_nombre', 'monto', 'fecha',
            'creado_por', 'creado_por_nombre', 'observaciones'
        ]
        read_only_fields = ['fecha', 'creado_por']
    
    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class FondoCajaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FondoCaja
        fields = ['empresa', 'monto', 'observaciones']
    
    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


# Transacciones
class TransaccionSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    metodo_pago_nombre = serializers.CharField(source='metodo_pago.nombre', read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = Transaccion
        fields = [
            'id', 'empresa', 'empresa_nombre', 'categoria', 'categoria_nombre',
            'metodo_pago', 'metodo_pago_nombre', 'tipo', 'monto',
            'descripcion', 'fecha', 'numero_comprobante', 'cierre_caja',
            'procesado_ia', 'confianza_ia'
        ]
        read_only_fields = ['fecha', 'cierre_caja', 'procesado_ia', 'confianza_ia']


class TransaccionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = [
            'empresa', 'categoria', 'metodo_pago', 'tipo',
            'monto', 'descripcion', 'numero_comprobante'
        ]
    
    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value
    
    def validate(self, data):
        # Validar que la categoría corresponda al tipo
        if data['categoria'].tipo != data['tipo']:
            raise serializers.ValidationError(
                f"La categoría '{data['categoria'].nombre}' no es válida para el tipo '{data['tipo']}'"
            )
        return data


# IA - Archivo
class ArchivoIASerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = ArchivoIA
        fields = [
            'id', 'empresa', 'empresa_nombre', 'archivo',
            'fecha_subida', 'estado', 'resultado_json', 'error_mensaje'
        ]
        read_only_fields = ['fecha_subida', 'estado', 'resultado_json', 'error_mensaje']


class ArchivoIAUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivoIA
        fields = ['empresa', 'archivo']
    
    def validate_archivo(self, value):
        # Validar extensión
        ext = value.name.split('.')[-1].lower()
        allowed = ['jpg', 'jpeg', 'png', 'pdf', 'xlsx', 'xls']
        if ext not in allowed:
            raise serializers.ValidationError(
                f"Formato no permitido. Permitidos: {', '.join(allowed)}"
            )
        
        # Validar tamaño (10MB max)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("El archivo no puede superar 10MB")
        
        return value


# IA - Resultados
class ResultadoIASerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoIA
        fields = [
            'id', 'archivo', 'tipo', 'monto', 'descripcion',
            'categoria_sugerida', 'metodo_pago_sugerido',
            'confianza', 'numero_comprobante',
            'convertido_transaccion', 'transaccion'
        ]
        read_only_fields = ['convertido_transaccion', 'transaccion']


class ResultadoIAListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar resultados"""
    archivo_id = serializers.IntegerField(source='archivo.id', read_only=True)
    # Los campos categoria_sugerida y metodo_pago_sugerido ya son strings (CharField)
    # así que usamos SerializerMethodField para mantener compatibilidad con el frontend
    categoria_sugerida_nombre = serializers.SerializerMethodField()
    metodo_pago_sugerido_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultadoIA
        fields = [
            'id', 'archivo_id', 'tipo', 'monto', 'descripcion',
            'categoria_sugerida', 'categoria_sugerida_nombre',
            'metodo_pago_sugerido', 'metodo_pago_sugerido_nombre',
            'confianza', 'numero_comprobante', 'convertido_transaccion'
        ]
    
    def get_categoria_sugerida_nombre(self, obj):
        """Retorna el nombre de la categoría (que ya es un string)"""
        return obj.categoria_sugerida
    
    def get_metodo_pago_sugerido_nombre(self, obj):
        """Retorna el nombre del método de pago (que ya es un string)"""
        return obj.metodo_pago_sugerido


class ResumenDiarioSerializer(serializers.Serializer):
    """Serializer para el resumen diario de transacciones"""
    ingresos = serializers.DecimalField(max_digits=10, decimal_places=2)
    egresos = serializers.DecimalField(max_digits=10, decimal_places=2)
    saldo = serializers.DecimalField(max_digits=10, decimal_places=2)