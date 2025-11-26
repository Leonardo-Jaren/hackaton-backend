from rest_framework import serializers
from core.serializers.base import BaseModelSerializer
from core.models import CategoriaTransaccion, MetodoPago


# --- Serializers de Entrada ---

class CrearCategoriaSerializer(serializers.Serializer):
    """Serializer para crear una nueva categoría de transacción."""
    nombre = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Nombre de la categoría (Ej. Venta, Sueldo)"
    )
    tipo = serializers.ChoiceField(
        choices=[('ingreso', 'Ingreso'), ('gasto', 'Egreso')],
        required=True,
        help_text="Tipo de categoría: ingreso o gasto"
    )

    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value.strip()


class CrearMetodoPagoSerializer(serializers.Serializer):
    """Serializer para crear un nuevo método de pago."""
    nombre = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Nombre del método de pago (Ej. Efectivo, Tarjeta, Yape)"
    )

    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value.strip()


# --- Serializers de Salida ---

class CategoriaTransaccionSerializer(BaseModelSerializer):
    """Serializer para mostrar información de categorías de transacción."""
    
    class Meta:
        model = CategoriaTransaccion
        fields = ['id', 'nombre', 'tipo']
        read_only_fields = ['id']


class MetodoPagoSerializer(BaseModelSerializer):
    """Serializer para mostrar información de métodos de pago."""
    
    class Meta:
        model = MetodoPago
        fields = ['id', 'nombre']
        read_only_fields = ['id']


# --- Serializers para Bulk Operations ---

class CrearCategoriasLoteSerializer(serializers.Serializer):
    """Serializer para crear múltiples categorías a la vez."""
    categorias = serializers.ListField(
        child=CrearCategoriaSerializer(),
        allow_empty=False,
        help_text="Lista de categorías a crear"
    )


class CrearMetodosPagoLoteSerializer(serializers.Serializer):
    """Serializer para crear múltiples métodos de pago a la vez."""
    metodos_pago = serializers.ListField(
        child=CrearMetodoPagoSerializer(),
        allow_empty=False,
        help_text="Lista de métodos de pago a crear"
    )
