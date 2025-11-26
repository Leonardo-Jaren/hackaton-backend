from .base import BaseRepository
from ..models import Transaccion, MetodoPago
from django.db.models import Sum, Q
from datetime import date
from typing import List, Optional
from decimal import Decimal


class TransaccionRepository(BaseRepository):
    model = Transaccion
    
    def obtener_transacciones_por_fecha(self, empresa_id: int, fecha: date):
        """Obtiene todas las transacciones de un día específico"""
        return self.filter(
            empresa_id=empresa_id,
            fecha__date=fecha
        ).select_related('categoria', 'metodo_pago')
    
    def obtener_ingresos_del_dia(self, empresa_id: int, fecha: date):
        """Obtiene solo los ingresos del día"""
        return self.filter(
            empresa_id=empresa_id,
            tipo='ingreso',
            fecha__date=fecha
        )
    
    def obtener_egresos_del_dia(self, empresa_id: int, fecha: date):
        """Obtiene solo los egresos del día"""
        return self.filter(
            empresa_id=empresa_id,
            tipo='egreso',
            fecha__date=fecha
        )
    
    def calcular_total_por_metodo_pago(self, empresa_id: int, fecha: date, metodo_pago_id: int) -> Decimal:
        """Calcula el total de transacciones por método de pago"""
        resultado = self.filter(
            empresa_id=empresa_id,
            fecha__date=fecha,
            metodo_pago_id=metodo_pago_id,
            tipo='ingreso'
        ).aggregate(total=Sum('monto'))
        return resultado['total'] or Decimal('0.00')
    
    def calcular_total_efectivo(self, empresa_id: int, fecha: date) -> Decimal:
        """Calcula el total de efectivo del día"""
        metodo_efectivo = MetodoPago.objects.filter(
            nombre__icontains='efectivo'
        ).first()
        
        if not metodo_efectivo:
            return Decimal('0.00')
            
        return self.calcular_total_por_metodo_pago(
            empresa_id, 
            fecha, 
            metodo_efectivo.id
        )
    
    def obtener_resumen_diario(self, empresa_id: int, fecha: date) -> dict:
        """Genera un resumen de ingresos y egresos del día"""
        ingresos = self.filter(
            empresa_id=empresa_id,
            tipo='ingreso',
            fecha__date=fecha
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        egresos = self.filter(
            empresa_id=empresa_id,
            tipo='egreso',
            fecha__date=fecha
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        return {
            'ingresos': ingresos,
            'egresos': egresos,
            'saldo': ingresos - egresos
        }
    
    def obtener_transacciones_sin_cierre(self, empresa_id: int):
        """Obtiene transacciones que aún no están asignadas a un cierre"""
        return self.filter(
            empresa_id=empresa_id,
            cierre_caja__isnull=True
        )
    
    def asignar_cierre(self, transaccion_ids: List[int], cierre_id: int) -> int:
        """
        Asigna un cierre de caja a múltiples transacciones
        
        Returns:
            Número de transacciones actualizadas
        """
        return self.filter(
            id__in=transaccion_ids
        ).update(cierre_caja_id=cierre_id)
    
    def obtener_por_categoria(self, empresa_id: int, fecha: date, categoria_id: int):
        """Obtiene transacciones por categoría"""
        return self.filter(
            empresa_id=empresa_id,
            fecha__date=fecha,
            categoria_id=categoria_id
        ).select_related('metodo_pago')
    
    def calcular_total_por_categoria(self, empresa_id: int, fecha: date) -> List[dict]:
        """Calcula totales agrupados por categoría"""
        from django.db.models import Sum, Count
        
        return list(
            self.filter(
                empresa_id=empresa_id,
                fecha__date=fecha
            )
            .values('categoria__nombre', 'tipo')
            .annotate(
                total=Sum('monto'),
                cantidad=Count('id')
            )
            .order_by('tipo', '-total')
        )