from core.repositories.core_repo import CategoriaTransaccionRepository, MetodoPagoRepository
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class CoreService:
    """
    Servicio de Core. Maneja la lógica de negocio relacionada con
    categorías de transacción y métodos de pago.
    """
    
    def __init__(
        self,
        categoria_repo: CategoriaTransaccionRepository = None,
        metodo_pago_repo: MetodoPagoRepository = None
    ):
        # Inyección de dependencias para facilitar testing
        self.categoria_repo = categoria_repo or CategoriaTransaccionRepository()
        self.metodo_pago_repo = metodo_pago_repo or MetodoPagoRepository()

    # --- Métodos para Categorías de Transacción ---

    @transaction.atomic
    def crear_categoria(self, nombre: str, tipo: str) -> dict:
        """
        Crea una nueva categoría de transacción.
        
        Args:
            nombre: Nombre de la categoría
            tipo: Tipo de categoría (ingreso/gasto)
            
        Returns:
            dict con información de la categoría creada
            
        Raises:
            ValueError: Si la categoría ya existe
        """
        # Verificar si ya existe
        categoria_existente = self.categoria_repo.get_by_nombre(nombre)
        if categoria_existente:
            raise ValueError(
                f"Ya existe una categoría con el nombre '{nombre}'. "
                f"ID: {categoria_existente.id}"
            )
        
        # Crear la categoría
        categoria = self.categoria_repo.create(nombre=nombre, tipo=tipo)
        
        logger.info(f"Categoría creada: {categoria.nombre} (ID: {categoria.id}, Tipo: {categoria.tipo})")
        
        return {
            'id': categoria.id,
            'nombre': categoria.nombre,
            'tipo': categoria.tipo,
            'mensaje': 'Categoría creada correctamente'
        }

    def listar_categorias(self, tipo: str = None) -> list:
        """
        Lista todas las categorías de transacción.
        
        Args:
            tipo: Filtro opcional por tipo (ingreso/gasto)
            
        Returns:
            Lista de categorías
        """
        if tipo:
            categorias = self.categoria_repo.get_by_tipo(tipo)
        else:
            categorias = self.categoria_repo.get_all()
        
        return categorias

    @transaction.atomic
    def crear_categorias_lote(self, categorias_data: list) -> dict:
        """
        Crea múltiples categorías de transacción en lote.
        Útil para scripts de inicialización.
        
        Args:
            categorias_data: Lista de diccionarios con nombre y tipo
            
        Returns:
            dict con resumen de categorías creadas y errores
        """
        creadas = []
        errores = []
        
        for categoria_data in categorias_data:
            try:
                categoria = self.categoria_repo.create_if_not_exists(
                    nombre=categoria_data['nombre'],
                    tipo=categoria_data['tipo']
                )
                creadas.append({
                    'id': categoria.id,
                    'nombre': categoria.nombre,
                    'tipo': categoria.tipo
                })
                logger.info(f"Categoría procesada: {categoria.nombre}")
            except Exception as e:
                error_msg = f"Error al crear '{categoria_data['nombre']}': {str(e)}"
                errores.append(error_msg)
                logger.error(error_msg)
        
        return {
            'total_procesadas': len(categorias_data),
            'creadas': len(creadas),
            'errores': len(errores),
            'categorias': creadas,
            'detalles_errores': errores
        }

    # --- Métodos para Métodos de Pago ---

    @transaction.atomic
    def crear_metodo_pago(self, nombre: str) -> dict:
        """
        Crea un nuevo método de pago.
        
        Args:
            nombre: Nombre del método de pago
            
        Returns:
            dict con información del método de pago creado
            
        Raises:
            ValueError: Si el método de pago ya existe
        """
        # Verificar si ya existe
        metodo_existente = self.metodo_pago_repo.get_by_nombre(nombre)
        if metodo_existente:
            raise ValueError(
                f"Ya existe un método de pago con el nombre '{nombre}'. "
                f"ID: {metodo_existente.id}"
            )
        
        # Crear el método de pago
        metodo_pago = self.metodo_pago_repo.create(nombre=nombre)
        
        logger.info(f"Método de pago creado: {metodo_pago.nombre} (ID: {metodo_pago.id})")
        
        return {
            'id': metodo_pago.id,
            'nombre': metodo_pago.nombre,
            'mensaje': 'Método de pago creado correctamente'
        }

    def listar_metodos_pago(self) -> list:
        """
        Lista todos los métodos de pago.
        
        Returns:
            Lista de métodos de pago
        """
        return self.metodo_pago_repo.get_all()

    @transaction.atomic
    def crear_metodos_pago_lote(self, metodos_data: list) -> dict:
        """
        Crea múltiples métodos de pago en lote.
        Útil para scripts de inicialización.
        
        Args:
            metodos_data: Lista de diccionarios con nombre
            
        Returns:
            dict con resumen de métodos de pago creados y errores
        """
        creados = []
        errores = []
        
        for metodo_data in metodos_data:
            try:
                metodo_pago = self.metodo_pago_repo.create_if_not_exists(
                    nombre=metodo_data['nombre']
                )
                creados.append({
                    'id': metodo_pago.id,
                    'nombre': metodo_pago.nombre
                })
                logger.info(f"Método de pago procesado: {metodo_pago.nombre}")
            except Exception as e:
                error_msg = f"Error al crear '{metodo_data['nombre']}': {str(e)}"
                errores.append(error_msg)
                logger.error(error_msg)
        
        return {
            'total_procesados': len(metodos_data),
            'creados': len(creados),
            'errores': len(errores),
            'metodos_pago': creados,
            'detalles_errores': errores
        }

    # --- Métodos de Inicialización ---

    @transaction.atomic
    def inicializar_datos_huanuco(self) -> dict:
        """
        Inicializa las categorías y métodos de pago típicos de Huánuco.
        Este método puede ser usado en scripts de inicialización.
        
        Returns:
            dict con resumen de la inicialización
        """
        # Categorías típicas
        categorias_default = [
            {'nombre': 'Venta', 'tipo': 'ingreso'},
            {'nombre': 'Servicio', 'tipo': 'ingreso'},
            {'nombre': 'Sueldo', 'tipo': 'gasto'},
            {'nombre': 'Compra de Insumos', 'tipo': 'gasto'},
            {'nombre': 'Servicios Básicos', 'tipo': 'gasto'},
            {'nombre': 'Alquiler', 'tipo': 'gasto'},
            {'nombre': 'Mantenimiento', 'tipo': 'gasto'},
            {'nombre': 'Otros Ingresos', 'tipo': 'ingreso'},
            {'nombre': 'Otros Gastos', 'tipo': 'gasto'},
        ]
        
        # Métodos de pago típicos en Huánuco
        metodos_default = [
            {'nombre': 'Efectivo'},
            {'nombre': 'Yape'},
            {'nombre': 'Plin'},
            {'nombre': 'Transferencia Bancaria'},
            {'nombre': 'Tarjeta de Crédito'},
            {'nombre': 'Tarjeta de Débito'},
            {'nombre': 'BCP'},
            {'nombre': 'Interbank'},
            {'nombre': 'BBVA'},
        ]
        
        resultado_categorias = self.crear_categorias_lote(categorias_default)
        resultado_metodos = self.crear_metodos_pago_lote(metodos_default)
        
        logger.info(
            f"Inicialización completada: "
            f"{resultado_categorias['creadas']} categorías, "
            f"{resultado_metodos['creados']} métodos de pago"
        )
        
        return {
            'categorias': resultado_categorias,
            'metodos_pago': resultado_metodos,
            'mensaje': 'Inicialización completada correctamente'
        }
