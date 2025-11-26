from django.core.exceptions import ValidationError
from django.db import transaction
from ..repositories.transaccion_repo import TransaccionRepository
from ..models import (
    Transaccion, MetodoPago, CategoriaTransaccion,
    FondoCaja, ArchivoIA, ResultadoIA, Empresa
)
from .gemini_service import GeminiService
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict
import os
import json


class TransaccionService:
    def __init__(self):
        self.repo = TransaccionRepository()
        self.gemini_service = GeminiService()
    
    # ==================== FONDO DE CAJA ====================
    
    def crear_fondo_caja(self, empresa_id: int, monto: Decimal, user, observaciones: str = "") -> FondoCaja:
        """Crea el fondo inicial de caja para el día"""
        # Validar que no exista un fondo para hoy
        hoy = date.today()
        existe = FondoCaja.objects.filter(
            empresa_id=empresa_id,
            fecha=hoy
        ).exists()
        
        if existe:
            raise ValidationError(
                f"Ya existe un fondo de caja para la empresa en la fecha {hoy}"
            )
        
        if monto <= 0:
            raise ValidationError("El monto del fondo debe ser mayor a 0")
        
        fondo = FondoCaja.objects.create(
            empresa_id=empresa_id,
            monto=monto,
            creado_por=user,
            observaciones=observaciones
        )
        
        return fondo
    
    # ==================== TRANSACCIONES MANUALES ====================
    
    def crear_transaccion(self, data: dict) -> Transaccion:
        """Crea una nueva transacción manual"""
        # Validar monto
        if data.get('monto', 0) <= 0:
            raise ValidationError("El monto de la transacción debe ser mayor a 0")
        
        # Validar que la categoría corresponda al tipo
        categoria_id = data['categoria'].id if hasattr(data['categoria'], 'id') else data['categoria']
        categoria = CategoriaTransaccion.objects.get(id=categoria_id)
        
        if categoria.tipo != data['tipo']:
            raise ValidationError(
                f"La categoría '{categoria.nombre}' no es válida para el tipo '{data['tipo']}'"
            )
        
        return self.repo.create(**data)
    
    def obtener_transacciones_dia(self, empresa_id: int, fecha: date = None):
        """Obtiene transacciones del día (por defecto hoy)"""
        if fecha is None:
            fecha = date.today()
        return self.repo.obtener_transacciones_por_fecha(empresa_id, fecha)
    
    def obtener_resumen_dia(self, empresa_id: int, fecha: date = None) -> Dict:
        """Genera resumen diario"""
        if fecha is None:
            fecha = date.today()
        return self.repo.obtener_resumen_diario(empresa_id, fecha)
    
    # ==================== PROCESAMIENTO IA ====================
    
    def procesar_archivo_ia(self, archivo_id: int) -> ArchivoIA:
        """
        Procesa un archivo subido usando la API de GPT-4o
        """
        archivo = None
        try:
            archivo = ArchivoIA.objects.get(id=archivo_id)
            archivo.estado = 'procesando'
            archivo.save()
            
            # Leer el archivo
            file_path = archivo.archivo.path
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Llamar a la API de OpenAI según el tipo de archivo
            if file_ext in ['.jpg', '.jpeg', '.png']:
                resultado = self._procesar_imagen(file_path, archivo.empresa)
            elif file_ext == '.pdf':
                resultado = self._procesar_pdf(file_path, archivo.empresa)
            elif file_ext in ['.xlsx', '.xls']:
                resultado = self._procesar_excel(file_path, archivo.empresa)
            else:
                raise ValidationError(f"Formato de archivo no soportado: {file_ext}")
            
            # Guardar resultados
            archivo.resultado_json = resultado
            archivo.estado = 'completado'
            archivo.save()
            
            # Crear registros de ResultadoIA (sin transaction.atomic para evitar bloqueos)
            self._crear_resultados_ia(archivo, resultado)
            
            return archivo
            
        except Exception as e:
            import traceback
            error_completo = traceback.format_exc()
            print(f"❌ ERROR procesando archivo: {e}")
            print(error_completo)
            
            if archivo:
                archivo.estado = 'error'
                archivo.error_mensaje = str(e)[:500]  # Limitar tamaño
                try:
                    archivo.save()
                except:
                    pass  # Si no puede guardar, al menos no rompa todo
            raise ValidationError(f"Error procesando archivo: {str(e)}")
    
    def _procesar_imagen(self, file_path: str, empresa: Empresa) -> dict:
        """Procesa una imagen usando Google Gemini"""
        try:
            return self.gemini_service.procesar_imagen_comprobante(file_path, empresa)
        except Exception as e:
            raise ValidationError(f"Error al procesar imagen con Gemini: {str(e)}")
    
    def _procesar_pdf(self, file_path: str, empresa: Empresa) -> dict:
        """Procesa un PDF (implementar según necesidad)"""
        # TODO: Implementar extracción de texto del PDF y procesamiento con Gemini
        raise ValidationError("Procesamiento de PDF aún no implementado")
    
    def _procesar_excel(self, file_path: str, empresa: Empresa) -> dict:
        """Procesa un archivo Excel con Google Gemini"""
        try:
            return self.gemini_service.procesar_excel_transacciones(file_path, empresa)
        except Exception as e:
            raise ValidationError(f"Error al procesar Excel con Gemini: {str(e)}")
    
    def _crear_resultados_ia(self, archivo: ArchivoIA, resultado: dict):
        """Crea registros de ResultadoIA a partir del JSON"""
        transacciones = resultado.get('transacciones', [])
        
        print(f"📊 Creando {len(transacciones)} resultados de IA...")
        print(f"🔍 Primer resultado para debug: {transacciones[0] if transacciones else 'VACIO'}")
        
        created_count = 0
        for i, trans in enumerate(transacciones, 1):
            try:
                # Verificar que trans sea un diccionario
                if trans is None:
                    print(f"   ⚠️ Resultado #{i} es None, saltando...")
                    continue
                
                if not isinstance(trans, dict):
                    print(f"   ⚠️ Resultado #{i} no es dict: {type(trans)}, valor: {trans}")
                    continue
                
                # Extraer valores con validación
                tipo = trans.get('tipo', 'ingreso') if isinstance(trans.get('tipo'), str) else 'ingreso'
                monto_raw = trans.get('monto', 0)
                monto = Decimal(str(monto_raw)) if monto_raw is not None else Decimal('0')
                descripcion = str(trans.get('descripcion', ''))[:500]
                categoria = str(trans.get('categoria_sugerida', ''))[:100]
                metodo = str(trans.get('metodo_pago_sugerido', 'Efectivo'))[:100]
                confianza_raw = trans.get('confianza', 0)
                confianza = Decimal(str(confianza_raw)) if confianza_raw is not None else Decimal('0')
                comprobante = str(trans.get('numero_comprobante', ''))[:50]
                
                ResultadoIA.objects.create(
                    archivo=archivo,
                    tipo=tipo,
                    monto=monto,
                    descripcion=descripcion,
                    categoria_sugerida=categoria,
                    metodo_pago_sugerido=metodo,
                    confianza=confianza,
                    numero_comprobante=comprobante
                )
                created_count += 1
                if i % 10 == 0:
                    print(f"   ✓ Creados {i}/{len(transacciones)}...")
            except Exception as e:
                import traceback
                print(f"   ✗ Error creando resultado #{i}: {e}")
                print(f"   📋 Datos del resultado: {trans}")
                print(f"   🔍 Traceback: {traceback.format_exc()}")
                # Continuar con el siguiente
                continue
        
        print(f"✅ Total creados: {created_count}/{len(transacciones)}")
    
    def obtener_resultados_ia(self, archivo_id: int = None, empresa_id: int = None):
        """Obtiene resultados de IA pendientes de conversión"""
        queryset = ResultadoIA.objects.filter(convertido_transaccion=False)
        
        if archivo_id:
            queryset = queryset.filter(archivo_id=archivo_id)
        
        if empresa_id:
            queryset = queryset.filter(archivo__empresa_id=empresa_id)
        
        return queryset.select_related('archivo')
    
    @transaction.atomic
    def convertir_resultado_a_transaccion(self, resultado_id: int) -> Transaccion:
        """Convierte un ResultadoIA en una Transacción real"""
        resultado = ResultadoIA.objects.get(id=resultado_id)
        
        if resultado.convertido_transaccion:
            raise ValidationError("Este resultado ya fue convertido a transacción")
        
        # Buscar o crear categoría
        categoria, _ = CategoriaTransaccion.objects.get_or_create(
            nombre=resultado.categoria_sugerida,
            defaults={'tipo': resultado.tipo}
        )
        
        # Buscar o crear método de pago
        metodo, _ = MetodoPago.objects.get_or_create(
            nombre=resultado.metodo_pago_sugerido
        )
        
        # Crear transacción
        transaccion = Transaccion.objects.create(
            empresa=resultado.archivo.empresa,
            categoria=categoria,
            metodo_pago=metodo,
            tipo=resultado.tipo,
            monto=resultado.monto,
            descripcion=resultado.descripcion,
            numero_comprobante=resultado.numero_comprobante,
            procesado_ia=True,
            confianza_ia=resultado.confianza
        )
        
        # Marcar resultado como convertido
        resultado.convertido_transaccion = True
        resultado.transaccion = transaccion
        resultado.save()
        
        return transaccion