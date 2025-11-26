from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime, date

from ..models import (
    Transaccion,
)
from ..serializers.transaccion_serializers import (
    TransaccionSerializer,
    TransaccionCreateSerializer,
    FondoCajaSerializer,
    FondoCajaCreateSerializer,
    ArchivoIASerializer,
    ArchivoIAUploadSerializer,
    ResultadoIAListSerializer,
    ResultadoIASerializer
)
from ..services.transaccion_service import TransaccionService


# ============================================
# FONDO DE CAJA
# ============================================

class FondoCajaCreateView(APIView):
    """
    POST /api/v1/transacciones/fondo-caja/
    Crear el Saldo Inicial (Fondo de Caja)
    
    Body:
    {
        "empresa": 1,
        "monto": 500.00,
        "observaciones": "Fondo inicial del día"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TransaccionService()
    
    def post(self, request):
        serializer = FondoCajaCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fondo = self.service.crear_fondo_caja(
                empresa_id=serializer.validated_data['empresa'].id,
                monto=serializer.validated_data['monto'],
                user=request.user,
                observaciones=serializer.validated_data.get('observaciones', '')
            )
            
            response_serializer = FondoCajaSerializer(fondo)
            return Response(
                {
                    'message': 'Fondo de caja creado exitosamente',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================
# TRANSACCIONES MANUALES
# ============================================

class TransaccionRegistroView(APIView):
    """
    POST /api/v1/transacciones/registro/
    Registrar una Transacción Manual
    
    Body:
    {
        "empresa": 1,
        "categoria": 2,
        "metodo_pago": 1,
        "tipo": "ingreso",
        "monto": 150.50,
        "descripcion": "Venta de productos",
        "numero_comprobante": "B001-00123"
    }
    
    GET /api/v1/transacciones/registro/?empresa_id=1&fecha=2025-11-26
    Obtener todas las Transacciones del día
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TransaccionService()
    
    def post(self, request):
        serializer = TransaccionCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            transaccion = self.service.crear_transaccion(serializer.validated_data)
            response_serializer = TransaccionSerializer(transaccion)
            
            return Response(
                {
                    'message': 'Transacción registrada exitosamente',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get(self, request):
        empresa_id = request.query_params.get('empresa_id')
        fecha_str = request.query_params.get('fecha')
        
        if not empresa_id:
            return Response(
                {'error': 'Debe proporcionar empresa_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parsear fecha (opcional, por defecto hoy)
        fecha = date.today()
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        transacciones = self.service.obtener_transacciones_dia(int(empresa_id), fecha)
        resumen = self.service.obtener_resumen_dia(int(empresa_id), fecha)
        
        serializer = TransaccionSerializer(transacciones, many=True)
        
        return Response({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'empresa_id': empresa_id,
            'total_transacciones': len(serializer.data),
            'resumen': resumen,
            'transacciones': serializer.data
        })


class TransaccionDetailView(APIView):
    """
    PUT /api/v1/transacciones/registro/<pk>/
    Actualizar una transacción
    
    DELETE /api/v1/transacciones/registro/<pk>/
    Eliminar una transacción
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        try:
            transaccion = Transaccion.objects.get(pk=pk)
        except Transaccion.DoesNotExist:
            return Response({'error': 'Transacción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TransaccionCreateSerializer(transaccion, data=request.data)
        
        if serializer.is_valid():
            transaccion = serializer.save()
            return Response(
                {
                    'message': 'Transacción actualizada exitosamente',
                    'data': TransaccionSerializer(transaccion).data
                }
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            transaccion = Transaccion.objects.get(pk=pk)
        except Transaccion.DoesNotExist:
            return Response({'error': 'Transacción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        transaccion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================
# PROCESAMIENTO IA
# ============================================

class CargaDataIAView(APIView):
    """
    POST /api/v1/transacciones/carga-data/
    Subir archivo/foto para procesamiento de IA
    
    Form-data:
    - empresa: 1
    - archivo: [file]
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TransaccionService()
    
    def post(self, request):
        serializer = ArchivoIAUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Guardar archivo
            archivo = serializer.save()
            
            # Procesar de forma asíncrona (en producción usar Celery)
            # Por ahora procesamos de forma síncrona
            archivo_procesado = self.service.procesar_archivo_ia(archivo.id)
            
            response_serializer = ArchivoIASerializer(archivo_procesado)
            
            return Response(
                {
                    'message': 'Archivo procesado exitosamente',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResultadosIAView(APIView):
    """
    GET /api/v1/transacciones/resultados-ia/?archivo_id=1&empresa_id=1
    Obtener los resultados del procesamiento de la IA
    
    POST /api/v1/transacciones/resultados-ia/convertir/
    Convertir un resultado de IA en transacción
    Body: { "resultado_id": 5 }
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TransaccionService()
    
    def get(self, request):
        archivo_id = request.query_params.get('archivo_id')
        empresa_id = request.query_params.get('empresa_id')
        
        resultados = self.service.obtener_resultados_ia(
            archivo_id=int(archivo_id) if archivo_id else None,
            empresa_id=int(empresa_id) if empresa_id else None
        )
        
        serializer = ResultadoIAListSerializer(resultados, many=True)
        
        return Response({
            'total_resultados': len(serializer.data),
            'resultados': serializer.data
        })
    
    def post(self, request):
        resultado_id = request.data.get('resultado_id')
        
        if not resultado_id:
            return Response(
                {'error': 'Debe proporcionar resultado_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            transaccion = self.service.convertir_resultado_a_transaccion(int(resultado_id))
            serializer = TransaccionSerializer(transaccion)
            
            return Response(
                {
                    'message': 'Resultado convertido a transacción exitosamente',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )