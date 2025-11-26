from cierre_caja.repositories.cierre_caja_repo import (
    CierreCajaRepository,
    ResumenEfectivoRepository,
    ResumenMetodoPagoRepository,
    ResultadoCuadreRepository,
    TransaccionRepository,
    FondoCajaRepository
)
from core.models import MetodoPago
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class CierreCajaService:
    """
    Servicio de Cierre de Caja. Maneja toda la lógica de negocio relacionada
    con el proceso de cierre de caja.
    """
    
    def __init__(
        self,
        cierre_repo: CierreCajaRepository = None,
        efectivo_repo: ResumenEfectivoRepository = None,
        metodo_pago_repo: ResumenMetodoPagoRepository = None,
        resultado_repo: ResultadoCuadreRepository = None,
        fondo_repo: FondoCajaRepository = None
    ):
        # Inyección de dependencias para facilitar testing
        self.cierre_repo = cierre_repo or CierreCajaRepository()
        self.efectivo_repo = efectivo_repo or ResumenEfectivoRepository()
        self.metodo_pago_repo = metodo_pago_repo or ResumenMetodoPagoRepository()
        self.resultado_repo = resultado_repo or ResultadoCuadreRepository()
        self.fondo_repo = fondo_repo or FondoCajaRepository()

    @transaction.atomic
    def iniciar_cierre(self, fondo_caja_id: int, usuario_id: int) -> dict:
        """
        Inicia un nuevo proceso de cierre de caja.
        
        Args:
            fondo_caja_id: ID del FondoCaja utilizado
            usuario_id: ID del usuario que inicia el cierre
            
        Returns:
            dict con información del cierre creado
            
        Raises:
            ValueError: Si el fondo no existe o ya hay un cierre abierto
        """
        # 1. Verificar que el fondo existe
        fondo_caja = self.fondo_repo.get_by_id_with_cajero(fondo_caja_id)
        if not fondo_caja:
            raise ValueError(f"El FondoCaja con ID {fondo_caja_id} no existe.")
        
        # 2. Verificar que el usuario que inicia es el dueño del fondo
        if fondo_caja.cajero_id != usuario_id:
            raise ValueError("Solo el cajero propietario del fondo puede iniciar el cierre.")
        
        # 3. Verificar que no haya un cierre abierto
        cierre_existente = self.cierre_repo.get_cierre_abierto_by_cajero(usuario_id)
        if cierre_existente:
            raise ValueError(
                f"Ya existe un cierre abierto (ID: {cierre_existente.id}). "
                "Debe finalizarlo antes de iniciar uno nuevo."
            )
        
        # 4. Crear el nuevo cierre
        cierre = self.cierre_repo.create(
            cajero_id=usuario_id,
            empresa_id=fondo_caja.cajero.empresa_id,
            fondo_inicial_id=fondo_caja_id,
            estado='abierto'
        )
        
        logger.info(f"Cierre de caja iniciado: ID {cierre.id} por cajero {usuario_id}")
        
        return {
            'cierre_id': cierre.id,
            'estado': cierre.estado,
            'fondo_inicial': fondo_caja.monto_inicial,
            'mensaje': 'Cierre de caja iniciado correctamente'
        }

    def obtener_resumen_cierre(self, cierre_id: int, usuario_id: int) -> dict:
        """
        Obtiene el resumen del cierre con los totales esperados del sistema
        (antes del conteo físico).
        
        Args:
            cierre_id: ID del cierre de caja
            usuario_id: ID del usuario que solicita el resumen
            
        Returns:
            dict con el resumen del cierre
            
        Raises:
            ValueError: Si el cierre no existe o no pertenece al usuario
        """
        # 1. Obtener el cierre
        cierre = self.cierre_repo.get_with_relations(cierre_id)
        if not cierre:
            raise ValueError(f"El cierre con ID {cierre_id} no existe.")
        
        # 2. Verificar permisos
        if cierre.cajero_id != usuario_id:
            raise ValueError("No tiene permisos para ver este cierre.")
        
        # 3. Calcular totales del sistema
        total_ingresos = TransaccionRepository.calcular_total_por_tipo_y_metodo(
            cajero_id=usuario_id,
            tipo='ingreso'
        )
        
        total_egresos = TransaccionRepository.calcular_total_por_tipo_y_metodo(
            cajero_id=usuario_id,
            tipo='gasto'
        )
        
        saldo_esperado = cierre.fondo_inicial.monto_inicial + total_ingresos - total_egresos
        
        # 4. Calcular ventas en efectivo
        ventas_efectivo = TransaccionRepository.calcular_ventas_efectivo(usuario_id)
        
        # 5. Obtener desglose por métodos de pago
        metodos_pago = MetodoPago.objects.all()
        metodos_detalle = []
        
        for metodo in metodos_pago:
            total_metodo = TransaccionRepository.calcular_total_por_tipo_y_metodo(
                cajero_id=usuario_id,
                tipo='ingreso',
                metodo_pago_id=metodo.id
            )
            
            if total_metodo > 0:  # Solo incluir métodos con transacciones
                metodos_detalle.append({
                    'metodo_id': metodo.id,
                    'metodo_nombre': metodo.nombre,
                    'total_sistema': float(total_metodo)
                })
        
        return {
            'cierre_id': cierre.id,
            'estado': cierre.estado,
            'fondo_inicial': float(cierre.fondo_inicial.monto_inicial),
            'total_ingresos': float(total_ingresos),
            'total_egresos': float(total_egresos),
            'saldo_esperado': float(saldo_esperado),
            'ventas_efectivo': float(ventas_efectivo),
            'metodos_pago': metodos_detalle
        }

    @transaction.atomic
    def registrar_conteo_efectivo(
        self,
        cierre_id: int,
        efectivo_contado: Decimal,
        usuario_id: int
    ) -> dict:
        """
        Registra el conteo físico de efectivo y calcula la diferencia.
        
        Args:
            cierre_id: ID del cierre de caja
            efectivo_contado: Monto de efectivo contado físicamente
            usuario_id: ID del usuario que registra el conteo
            
        Returns:
            dict con el resumen del efectivo
            
        Raises:
            ValueError: Si el cierre no existe, no está abierto o no pertenece al usuario
        """
        # 1. Obtener el cierre
        cierre = self.cierre_repo.get_by_id(cierre_id)
        if not cierre:
            raise ValueError(f"El cierre con ID {cierre_id} no existe.")
        
        # 2. Verificar permisos
        if cierre.cajero_id != usuario_id:
            raise ValueError("No tiene permisos para modificar este cierre.")
        
        # 3. Verificar que el cierre está abierto
        if cierre.estado != 'abierto':
            raise ValueError(
                f"El cierre está en estado '{cierre.estado}'. "
                "Solo se puede registrar efectivo en cierres abiertos."
            )
        
        # 4. Calcular ventas en efectivo según el sistema
        ventas_efectivo_sistema = TransaccionRepository.calcular_ventas_efectivo(usuario_id)
        
        # 5. Calcular diferencia
        diferencia = efectivo_contado - ventas_efectivo_sistema
        
        # 6. Verificar si ya existe un resumen de efectivo
        resumen_existente = self.efectivo_repo.get_by_cierre(cierre_id)
        
        if resumen_existente:
            # Actualizar el resumen existente
            self.efectivo_repo.update(
                resumen_existente,
                efectivo_contado_fisico=efectivo_contado,
                ventas_efectivo_sistema=ventas_efectivo_sistema,
                diferencia_efectivo=diferencia
            )
            resumen = resumen_existente
        else:
            # Crear nuevo resumen
            resumen = self.efectivo_repo.create(
                cierre_id=cierre_id,
                efectivo_contado_fisico=efectivo_contado,
                ventas_efectivo_sistema=ventas_efectivo_sistema,
                diferencia_efectivo=diferencia
            )
        
        logger.info(
            f"Efectivo registrado en cierre {cierre_id}: "
            f"Contado=${efectivo_contado}, Sistema=${ventas_efectivo_sistema}, "
            f"Diferencia=${diferencia}"
        )
        
        return {
            'resumen_id': resumen.id,
            'efectivo_contado_fisico': float(resumen.efectivo_contado_fisico),
            'ventas_efectivo_sistema': float(resumen.ventas_efectivo_sistema),
            'diferencia_efectivo': float(resumen.diferencia_efectivo),
            'mensaje': 'Conteo de efectivo registrado correctamente'
        }

    @transaction.atomic
    def finalizar_cierre(
        self,
        cierre_id: int,
        usuario_id: int,
        observaciones: str = None
    ) -> dict:
        """
        Finaliza el cierre de caja, calculando el resultado final y
        determinando si está cuadrado o descuadrado.
        
        Args:
            cierre_id: ID del cierre de caja
            usuario_id: ID del usuario que finaliza el cierre
            observaciones: Observaciones adicionales sobre el cierre
            
        Returns:
            dict con el resultado del cierre
            
        Raises:
            ValueError: Si el cierre no existe, no está abierto o faltan datos
        """
        # 1. Obtener el cierre
        cierre = self.cierre_repo.get_with_relations(cierre_id)
        if not cierre:
            raise ValueError(f"El cierre con ID {cierre_id} no existe.")
        
        # 2. Verificar permisos
        if cierre.cajero_id != usuario_id:
            raise ValueError("No tiene permisos para finalizar este cierre.")
        
        # 3. Verificar que el cierre está abierto
        if cierre.estado != 'abierto':
            raise ValueError(
                f"El cierre está en estado '{cierre.estado}'. "
                "Solo se pueden finalizar cierres abiertos."
            )
        
        # 4. Verificar que se haya registrado el efectivo
        resumen_efectivo = self.efectivo_repo.get_by_cierre(cierre_id)
        if not resumen_efectivo:
            raise ValueError(
                "Debe registrar el conteo de efectivo antes de finalizar el cierre."
            )
        
        # 5. Calcular totales de faltantes y sobrantes
        faltante_total = Decimal('0.00')
        sobrante_total = Decimal('0.00')
        
        # Analizar diferencia de efectivo
        if resumen_efectivo.diferencia_efectivo < 0:
            faltante_total += abs(resumen_efectivo.diferencia_efectivo)
        elif resumen_efectivo.diferencia_efectivo > 0:
            sobrante_total += resumen_efectivo.diferencia_efectivo
        
        # Analizar diferencias de otros métodos de pago (si existen)
        resumenes_metodo = self.metodo_pago_repo.get_by_cierre(cierre_id)
        for resumen in resumenes_metodo:
            if resumen.diferencia < 0:
                faltante_total += abs(resumen.diferencia)
            elif resumen.diferencia > 0:
                sobrante_total += resumen.diferencia
        
        # 6. Determinar si es un encuadre perfecto
        es_encuadre_perfecto = (faltante_total == 0 and sobrante_total == 0)
        
        # 7. Determinar el estado final del cierre
        nuevo_estado = 'cuadrado' if es_encuadre_perfecto else 'descuadrado'
        
        # 8. Crear o actualizar resultado de cuadre
        resultado_existente = self.resultado_repo.get_by_cierre(cierre_id)
        
        if resultado_existente:
            self.resultado_repo.update(
                resultado_existente,
                es_encuadre_perfecto=es_encuadre_perfecto,
                faltante_total=faltante_total,
                sobrante_total=sobrante_total,
                observaciones=observaciones
            )
            resultado = resultado_existente
        else:
            resultado = self.resultado_repo.create(
                cierre_id=cierre_id,
                es_encuadre_perfecto=es_encuadre_perfecto,
                faltante_total=faltante_total,
                sobrante_total=sobrante_total,
                observaciones=observaciones
            )
        
        # 9. Actualizar el estado del cierre y registrar fecha de cierre
        self.cierre_repo.update(
            cierre,
            estado=nuevo_estado,
            fecha_cierre=timezone.now()
        )
        
        logger.info(
            f"Cierre {cierre_id} finalizado: Estado={nuevo_estado}, "
            f"Faltante=${faltante_total}, Sobrante=${sobrante_total}"
        )
        
        return {
            'cierre_id': cierre.id,
            'estado': nuevo_estado,
            'fecha_cierre': cierre.fecha_cierre.isoformat(),
            'es_encuadre_perfecto': es_encuadre_perfecto,
            'faltante_total': float(faltante_total),
            'sobrante_total': float(sobrante_total),
            'observaciones': observaciones,
            'mensaje': f'Cierre finalizado correctamente. Estado: {nuevo_estado}'
        }
