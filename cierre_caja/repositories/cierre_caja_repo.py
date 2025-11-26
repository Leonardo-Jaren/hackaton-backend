from cierre_caja.repositories.base import BaseRepository
from cierre_caja.models import CierreCaja, ResumenEfectivo, ResumenMetodoPago, ResultadoCuadre
from transacciones.models import FondoCaja, Transaccion
from core.models import MetodoPago
from django.db.models import Sum, Q
from decimal import Decimal


class CierreCajaRepository(BaseRepository):
    """Maneja la persistencia del modelo CierreCaja."""
    model = CierreCaja

    def get_cierre_abierto_by_cajero(self, cajero_id: int):
        """Obtiene el cierre de caja abierto del cajero."""
        return self.model.objects.filter(
            cajero_id=cajero_id,
            estado='abierto'
        ).first()

    def get_with_relations(self, cierre_id: int):
        """Obtiene un cierre con todas sus relaciones."""
        return self.model.objects.select_related(
            'cajero', 'empresa', 'fondo_inicial'
        ).prefetch_related(
            'resumenes_efectivo',
            'resumenes_metodo_pago',
            'resumenes_metodo_pago__metodo_pago',
            'resultados_cuadre'
        ).filter(pk=cierre_id).first()


class ResumenEfectivoRepository(BaseRepository):
    """Maneja la persistencia del modelo ResumenEfectivo."""
    model = ResumenEfectivo

    def get_by_cierre(self, cierre_id: int):
        """Obtiene el resumen de efectivo de un cierre."""
        return self.model.objects.filter(cierre_id=cierre_id).first()


class ResumenMetodoPagoRepository(BaseRepository):
    """Maneja la persistencia del modelo ResumenMetodoPago."""
    model = ResumenMetodoPago

    def get_by_cierre(self, cierre_id: int):
        """Obtiene todos los resúmenes de métodos de pago de un cierre."""
        return self.model.objects.filter(cierre_id=cierre_id).select_related('metodo_pago')

    def get_by_cierre_and_metodo(self, cierre_id: int, metodo_pago_id: int):
        """Obtiene el resumen de un método de pago específico."""
        return self.model.objects.filter(
            cierre_id=cierre_id,
            metodo_pago_id=metodo_pago_id
        ).first()


class ResultadoCuadreRepository(BaseRepository):
    """Maneja la persistencia del modelo ResultadoCuadre."""
    model = ResultadoCuadre

    def get_by_cierre(self, cierre_id: int):
        """Obtiene el resultado de cuadre de un cierre."""
        return self.model.objects.filter(cierre_id=cierre_id).first()


class TransaccionRepository:
    """Maneja consultas de transacciones para cierre de caja."""
    
    @staticmethod
    def get_transacciones_by_fondo(fondo_id: int):
        """Obtiene todas las transacciones asociadas a un fondo de caja."""
        return Transaccion.objects.filter(
            cajero__fondos_caja__id=fondo_id
        ).select_related('metodo_pago', 'categoria', 'cajero')

    @staticmethod
    def calcular_total_por_tipo_y_metodo(cajero_id: int, tipo: str, metodo_pago_id: int = None):
        """Calcula el total de transacciones por tipo y método de pago."""
        filters = Q(cajero_id=cajero_id, tipo=tipo)
        
        if metodo_pago_id:
            filters &= Q(metodo_pago_id=metodo_pago_id)
        
        result = Transaccion.objects.filter(filters).aggregate(
            total=Sum('monto')
        )
        
        return result['total'] or Decimal('0.00')

    @staticmethod
    def calcular_ventas_efectivo(cajero_id: int):
        """Calcula el total de ventas en efectivo."""
        metodo_efectivo = MetodoPago.objects.filter(nombre__iexact='efectivo').first()
        
        if not metodo_efectivo:
            return Decimal('0.00')
        
        return TransaccionRepository.calcular_total_por_tipo_y_metodo(
            cajero_id=cajero_id,
            tipo='ingreso',
            metodo_pago_id=metodo_efectivo.id
        )


class FondoCajaRepository(BaseRepository):
    """Maneja la persistencia del modelo FondoCaja."""
    model = FondoCaja

    def get_by_id_with_cajero(self, fondo_id: int):
        """Obtiene un fondo de caja con información del cajero."""
        return self.model.objects.select_related('cajero').filter(pk=fondo_id).first()
