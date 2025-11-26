from cierre_caja.views.base import BaseAPIView
from cierre_caja.serializers.cierre_caja_serializers import (
    IniciarCierreSerializer,
    RegistrarEfectivoSerializer,
    FinalizarCierreSerializer,
    CierreCajaDetalleSerializer,
    ResumenCierreSerializer
)
from cierre_caja.services.cierre_caja_service import CierreCajaService
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class IniciarCierreView(BaseAPIView):
    """
    POST /api/cierre_caja/iniciar/
    
    Inicia un nuevo proceso de Cierre de Caja para el día/turno.
    Requiere el ID del FondoCaja usado.
    """
    
    def post(self, request):
        """Inicia un nuevo cierre de caja."""
        serializer = IniciarCierreSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = CierreCajaService()
            resultado = service.iniciar_cierre(
                fondo_caja_id=serializer.validated_data['fondo_caja_id'],
                usuario_id=request.user.id
            )
            
            return Response(resultado, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.warning(f"Error al iniciar cierre: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al iniciar cierre: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ObtenerResumenCierreView(BaseAPIView):
    """
    GET /api/cierre_caja/resumen/{id}/
    
    Obtener el Resumen del Cierre.
    Muestra los totales de ingresos/egresos del sistema 
    (la versión esperada antes del conteo físico).
    """
    
    def get(self, request, cierre_id):
        """Obtiene el resumen del cierre con los totales esperados."""
        try:
            service = CierreCajaService()
            resumen = service.obtener_resumen_cierre(
                cierre_id=cierre_id,
                usuario_id=request.user.id
            )
            
            serializer = ResumenCierreSerializer(resumen)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Error al obtener resumen de cierre: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error inesperado al obtener resumen: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegistrarEfectivoView(BaseAPIView):
    """
    PATCH /api/cierre_caja/efectivo/{id}/
    
    Registrar el Conteo Físico de Efectivo.
    Permite ingresar el monto de efectivo contado en la caja,
    desencadenando el cálculo de la diferencia (faltante/sobrante).
    """
    
    def patch(self, request, cierre_id):
        """Registra el conteo físico de efectivo."""
        serializer = RegistrarEfectivoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = CierreCajaService()
            resultado = service.registrar_conteo_efectivo(
                cierre_id=cierre_id,
                efectivo_contado=Decimal(str(serializer.validated_data['efectivo_contado_fisico'])),
                usuario_id=request.user.id
            )
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Error al registrar efectivo: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al registrar efectivo: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FinalizarCierreView(BaseAPIView):
    """
    POST /api/cierre_caja/finalizar/{id}/
    
    Cerrar y Documentar el Cierre.
    Marca el cierre como finalizado (cuadrado o descuadrado) 
    y guarda el resultado definitivo.
    """
    
    def post(self, request, cierre_id):
        """Finaliza el cierre de caja."""
        serializer = FinalizarCierreSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = CierreCajaService()
            resultado = service.finalizar_cierre(
                cierre_id=cierre_id,
                usuario_id=request.user.id,
                observaciones=serializer.validated_data.get('observaciones')
            )
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Error al finalizar cierre: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al finalizar cierre: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DetalleCierreView(BaseAPIView):
    """
    GET /api/cierre_caja/detalle/{id}/
    
    Obtiene el detalle completo de un cierre de caja con todos sus resúmenes.
    (Endpoint adicional útil para ver toda la información del cierre)
    """
    
    def get(self, request, cierre_id):
        """Obtiene el detalle completo de un cierre."""
        try:
            from cierre_caja.repositories.cierre_caja_repo import CierreCajaRepository
            
            repo = CierreCajaRepository()
            cierre = repo.get_with_relations(cierre_id)
            
            if not cierre:
                return Response(
                    {'error': f'El cierre con ID {cierre_id} no existe.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar permisos
            if cierre.cajero_id != request.user.id:
                return Response(
                    {'error': 'No tiene permisos para ver este cierre.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = CierreCajaDetalleSerializer(cierre)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error al obtener detalle del cierre: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
