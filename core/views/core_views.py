from core.views.base import BaseAPIView
from core.serializers.core_serializers import (
    CrearCategoriaSerializer,
    CrearMetodoPagoSerializer,
    CategoriaTransaccionSerializer,
    MetodoPagoSerializer,
    CrearCategoriasLoteSerializer,
    CrearMetodosPagoLoteSerializer
)
from core.services.core_service import CoreService
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)


# --- Vistas para Categorías de Transacción ---

class CrearCategoriaView(BaseAPIView):
    """
    POST /api/core/categorias/
    
    Crear una nueva Categoría de Transacción.
    Útil para agregar categorías personalizadas.
    """
    
    def post(self, request):
        """Crea una nueva categoría de transacción."""
        serializer = CrearCategoriaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = CoreService()
            resultado = service.crear_categoria(
                nombre=serializer.validated_data['nombre'],
                tipo=serializer.validated_data['tipo']
            )
            
            return Response(resultado, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.warning(f"Error al crear categoría: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al crear categoría: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListarCategoriasView(BaseAPIView):
    """
    GET /api/core/categorias/
    
    Obtener listado de Categorías de Transacción.
    Opcionalmente filtrar por tipo (ingreso/gasto).
    """
    
    def get(self, request):
        """Lista todas las categorías de transacción."""
        try:
            # Obtener parámetro de filtro opcional
            tipo = request.query_params.get('tipo', None)
            
            if tipo and tipo not in ['ingreso', 'gasto']:
                return Response(
                    {'error': "El tipo debe ser 'ingreso' o 'gasto'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            service = CoreService()
            categorias = service.listar_categorias(tipo=tipo)
            
            serializer = CategoriaTransaccionSerializer(categorias, many=True)
            
            return Response({
                'total': len(categorias),
                'categorias': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error al listar categorías: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CrearCategoriasLoteView(BaseAPIView):
    """
    POST /api/core/categorias/lote/
    
    Crear múltiples categorías en lote.
    Útil para scripts de inicialización.
    """
    
    def post(self, request):
        """Crea múltiples categorías de transacción."""
        serializer = CrearCategoriasLoteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = CoreService()
            resultado = service.crear_categorias_lote(
                categorias_data=serializer.validated_data['categorias']
            )
            
            return Response(resultado, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error al crear categorías en lote: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- Vistas para Métodos de Pago ---

class CrearMetodoPagoView(BaseAPIView):
    """
    POST /api/core/metodos-pago/
    
    Crear un nuevo Método de Pago.
    Útil para agregar métodos de pago personalizados.
    """
    
    def post(self, request):
        """Crea un nuevo método de pago."""
        serializer = CrearMetodoPagoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = CoreService()
            resultado = service.crear_metodo_pago(
                nombre=serializer.validated_data['nombre']
            )
            
            return Response(resultado, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.warning(f"Error al crear método de pago: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al crear método de pago: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListarMetodosPagoView(BaseAPIView):
    """
    GET /api/core/metodos-pago/
    
    Obtener listado de Métodos de Pago disponibles.
    """
    
    def get(self, request):
        """Lista todos los métodos de pago."""
        try:
            service = CoreService()
            metodos_pago = service.listar_metodos_pago()
            
            serializer = MetodoPagoSerializer(metodos_pago, many=True)
            
            return Response({
                'total': len(metodos_pago),
                'metodos_pago': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error al listar métodos de pago: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CrearMetodosPagoLoteView(BaseAPIView):
    """
    POST /api/core/metodos-pago/lote/
    
    Crear múltiples métodos de pago en lote.
    Útil para scripts de inicialización.
    """
    
    def post(self, request):
        """Crea múltiples métodos de pago."""
        serializer = CrearMetodosPagoLoteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = CoreService()
            resultado = service.crear_metodos_pago_lote(
                metodos_data=serializer.validated_data['metodos_pago']
            )
            
            return Response(resultado, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error al crear métodos de pago en lote: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- Vista de Inicialización ---

class InicializarDatosView(BaseAPIView):
    """
    POST /api/core/inicializar/
    
    Inicializar categorías y métodos de pago por defecto de Huánuco.
    Endpoint útil para configuración inicial del sistema.
    """
    
    # Permitir acceso sin autenticación para scripts de inicialización
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        """Inicializa los datos por defecto."""
        try:
            service = CoreService()
            resultado = service.inicializar_datos_huanuco()
            
            return Response(resultado, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error al inicializar datos: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor', 'detalle': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
