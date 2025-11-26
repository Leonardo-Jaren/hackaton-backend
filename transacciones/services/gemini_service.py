"""
Servicio de IA con OpenAI (ChatGPT) para procesamiento de transacciones
Funcionalidades principales:
1. Extracción de datos de imágenes (tickets, facturas, comprobantes)
2. Procesamiento de archivos Excel con transacciones
3. Clasificación automática de transacciones
4. Validación y corrección de datos
5. Sugerencias inteligentes de categorías y métodos de pago
"""

import os
import json
import base64
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date
from openai import OpenAI
from django.core.exceptions import ValidationError
from django.conf import settings

from ..models import (
    Empresa, CategoriaTransaccion, MetodoPago,
    ArchivoIA, ResultadoIA
)


class GeminiService:
    """Servicio para integración con OpenAI ChatGPT"""
    
    def __init__(self):
        """Inicializa el servicio con la API key de OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            raise ValidationError("OPENAI_API_KEY no está configurada")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Modelo principal con visión
        self.model_text = "gpt-4o-mini"  # Modelo para tareas de solo texto
    
    # ==================== FUNCIONES PRINCIPALES ====================
    
    def procesar_imagen_comprobante(self, image_path: str, empresa: Empresa) -> Dict:
        """
        FUNCIÓN 1: Extrae información de tickets, facturas o comprobantes
        
        Casos de uso:
        - Foto de ticket de venta
        - Factura escaneada
        - Comprobante de pago
        - Boleta de servicio
        
        Returns:
            Dict con transacciones detectadas y metadatos
        """
        try:
            # Leer y codificar la imagen en base64
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Crear prompt especializado para comprobantes peruanos
            prompt = self._crear_prompt_comprobante(empresa)
            
            # Procesar con GPT-4o Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            # Parsear respuesta JSON
            resultado = self._parse_json_response(response.choices[0].message.content)
            
            # Validar y enriquecer datos
            resultado = self._validar_y_enriquecer(resultado, empresa)
            
            return resultado
            
        except Exception as e:
            raise ValidationError(f"Error al procesar imagen: {str(e)}")
    
    def procesar_excel_transacciones(self, excel_path: str, empresa: Empresa) -> Dict:
        """
        FUNCIÓN 2: Procesa archivos Excel con transacciones
        
        Casos de uso:
        - Exportación de banco con movimientos
        - Planilla manual de ventas
        - Reporte de gastos
        
        Returns:
            Dict con transacciones normalizadas
        """
        try:
            import pandas as pd
            
            # Leer Excel
            df = pd.read_excel(excel_path)
            
            # Convertir a texto estructurado
            excel_text = self._dataframe_to_structured_text(df)
            
            # Crear prompt para Excel
            prompt = self._crear_prompt_excel(empresa, excel_text)
            
            # Procesar con GPT-4
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[
                    {"role": "system", "content": "Eres un experto contador peruano especializado en análisis de datos financieros."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            # Parsear respuesta
            resultado = self._parse_json_response(response.choices[0].message.content)
            
            # Validar y enriquecer
            resultado = self._validar_y_enriquecer(resultado, empresa)
            
            return resultado
            
        except Exception as e:
            raise ValidationError(f"Error al procesar Excel: {str(e)}")
    
    def clasificar_transaccion(self, descripcion: str, monto: Decimal, empresa: Empresa) -> Dict:
        """
        FUNCIÓN 3: Clasifica una transacción basándose en su descripción
        
        Casos de uso:
        - Usuario ingresa transacción manual sin categoría
        - Importación de datos sin clasificar
        - Sugerencias en tiempo real
        
        Returns:
            Dict con categoría y método de pago sugeridos + confianza
        """
        try:
            # Obtener categorías existentes
            categorias_existentes = list(
                CategoriaTransaccion.objects.values_list('nombre', 'tipo')
            )
            
            metodos_existentes = list(
                MetodoPago.objects.values_list('nombre', flat=True)
            )
            
            prompt = f"""
            Clasifica esta transacción para la empresa "{empresa.nombre}" ({empresa.regimen_tributario}):
            
            Descripción: {descripcion}
            Monto: S/ {monto}
            
            Categorías disponibles: {categorias_existentes}
            Métodos de pago disponibles: {metodos_existentes}
            
            Devuelve un JSON con:
            {{
                "tipo": "ingreso" o "gasto",
                "categoria_sugerida": "nombre de la categoría más apropiada",
                "metodo_pago_sugerido": "método de pago más probable",
                "confianza": porcentaje 0-100,
                "razon": "breve explicación de la clasificación"
            }}
            
            Si no existe una categoría apropiada, sugiere crear una nueva.
            """
            
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[
                    {"role": "system", "content": "Eres un experto contador peruano clasificando transacciones."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            resultado = self._parse_json_response(response.choices[0].message.content)
            
            return resultado
            
        except Exception as e:
            raise ValidationError(f"Error al clasificar transacción: {str(e)}")
    
    def validar_y_corregir_transaccion(self, transaccion_data: Dict, empresa: Empresa) -> Dict:
        """
        FUNCIÓN 4: Valida y corrige datos de una transacción
        
        Casos de uso:
        - Detectar montos anómalos
        - Corregir formatos de fecha
        - Validar números de comprobante
        - Detectar duplicados
        
        Returns:
            Dict con correcciones sugeridas
        """
        try:
            prompt = f"""
            Valida y corrige esta transacción para "{empresa.nombre}":
            
            Datos: {json.dumps(transaccion_data, indent=2)}
            
            Verifica:
            1. El monto está en rango razonable (no muy alto ni muy bajo)
            2. La descripción tiene sentido
            3. El número de comprobante sigue formato válido peruano
            4. La categoría es coherente con el monto y descripción
            
            Devuelve JSON:
            {{
                "es_valida": true/false,
                "errores": ["lista de errores encontrados"],
                "correcciones_sugeridas": {{
                    "campo": "valor_corregido"
                }},
                "alertas": ["alertas importantes"],
                "confianza_validacion": 0-100
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[
                    {"role": "system", "content": "Eres un auditor financiero experto en validación de transacciones."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            resultado = self._parse_json_response(response.choices[0].message.content)
            
            return resultado
            
        except Exception as e:
            raise ValidationError(f"Error al validar transacción: {str(e)}")
    
    def generar_resumen_inteligente(self, transacciones: List[Dict], fecha: date, empresa: Empresa) -> Dict:
        """
        FUNCIÓN 5: Genera un resumen inteligente del día
        
        Casos de uso:
        - Reporte al final del día
        - Detección de patrones anómalos
        - Sugerencias de mejora
        
        Returns:
            Dict con análisis y recomendaciones
        """
        try:
            prompt = f"""
            Analiza estas transacciones del día {fecha} para "{empresa.nombre}":
            
            {json.dumps(transacciones, indent=2)}
            
            Proporciona:
            1. Resumen ejecutivo del día
            2. Patrones o anomalías detectadas
            3. Comparación con días típicos (si hay datos históricos)
            4. Recomendaciones de acción
            5. Alertas importantes
            
            Devuelve JSON:
            {{
                "resumen": "texto del resumen",
                "total_ingresos": monto,
                "total_egresos": monto,
                "saldo_neto": monto,
                "anomalias": ["lista de anomalías"],
                "recomendaciones": ["lista de recomendaciones"],
                "alertas": ["lista de alertas"],
                "tendencias": "análisis de tendencias",
                "confianza_analisis": 0-100
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[
                    {"role": "system", "content": "Eres un analista financiero experto en análisis de flujo de caja."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            resultado = self._parse_json_response(response.choices[0].message.content)
            
            return resultado
            
        except Exception as e:
            raise ValidationError(f"Error al generar resumen: {str(e)}")
    
    def sugerir_categorias_faltantes(self, empresa: Empresa, transacciones_recientes: List[Dict]) -> List[Dict]:
        """
        FUNCIÓN 6: Sugiere nuevas categorías basándose en el uso
        
        Casos de uso:
        - Optimizar catálogo de categorías
        - Detectar necesidades no cubiertas
        
        Returns:
            Lista de categorías sugeridas
        """
        try:
            categorias_actuales = list(
                CategoriaTransaccion.objects.filter(
                    nombre__in=[t.get('categoria') for t in transacciones_recientes if t.get('categoria')]
                ).values('nombre', 'tipo')
            )
            
            prompt = f"""
            Basándote en estas transacciones recientes de "{empresa.nombre}":
            
            {json.dumps(transacciones_recientes[:50], indent=2)}
            
            Categorías actuales: {categorias_actuales}
            
            Sugiere nuevas categorías que ayudarían a clasificar mejor las transacciones.
            
            Devuelve JSON:
            {{
                "categorias_sugeridas": [
                    {{
                        "nombre": "nombre de la categoría",
                        "tipo": "ingreso" o "gasto",
                        "descripcion": "para qué sirve",
                        "ejemplos": ["ejemplos de uso"],
                        "prioridad": "alta/media/baja"
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[
                    {"role": "system", "content": "Eres un consultor contable especializado en optimización de procesos."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            
            resultado = self._parse_json_response(response.choices[0].message.content)
            
            return resultado.get('categorias_sugeridas', [])
            
        except Exception as e:
            raise ValidationError(f"Error al sugerir categorías: {str(e)}")
    
    def detectar_duplicados(self, transaccion_nueva: Dict, transacciones_existentes: List[Dict]) -> Dict:
        """
        FUNCIÓN 7: Detecta posibles transacciones duplicadas
        
        Casos de uso:
        - Evitar registro doble de la misma transacción
        - Alertar al usuario sobre posibles duplicados
        
        Returns:
            Dict con duplicados potenciales y probabilidad
        """
        try:
            prompt = f"""
            Analiza si esta transacción nueva es duplicada:
            
            Nueva: {json.dumps(transaccion_nueva, indent=2)}
            
            Existentes (últimas 50):
            {json.dumps(transacciones_existentes[:50], indent=2)}
            
            Devuelve JSON:
            {{
                "es_duplicado": true/false,
                "probabilidad_duplicado": 0-100,
                "duplicados_potenciales": [
                    {{
                        "indice": numero,
                        "similitud": 0-100,
                        "razon": "por qué podría ser duplicado"
                    }}
                ],
                "recomendacion": "registrar/revisar/descartar"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[
                    {"role": "system", "content": "Eres un sistema de detección de duplicados en transacciones financieras."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            resultado = self._parse_json_response(response.choices[0].message.content)
            
            return resultado
            
        except Exception as e:
            raise ValidationError(f"Error al detectar duplicados: {str(e)}")
    
    # ==================== FUNCIONES AUXILIARES ====================
    
    def _crear_prompt_comprobante(self, empresa: Empresa) -> str:
        """Crea prompt optimizado para comprobantes peruanos"""
        return f"""
        Eres un experto contador peruano analizando comprobantes para "{empresa.nombre}".
        
        Extrae TODA la información de este comprobante y devuelve un JSON con:
        
        {{
            "tipo_comprobante": "boleta/factura/ticket/nota de crédito/etc",
            "emisor": "nombre del negocio emisor",
            "ruc_emisor": "RUC si está visible",
            "numero_comprobante": "número del comprobante",
            "fecha": "fecha en formato YYYY-MM-DD",
            "transacciones": [
                {{
                    "tipo": "ingreso" o "gasto",
                    "monto": número decimal (solo el total final),
                    "descripcion": "descripción detallada",
                    "categoria_sugerida": "categoría apropiada",
                    "metodo_pago_sugerido": "Efectivo/Tarjeta/Yape/Plin/Transferencia",
                    "confianza": porcentaje 0-100,
                    "items": ["lista de items si es aplicable"],
                    "subtotal": monto sin IGV,
                    "igv": monto de IGV,
                    "total": monto total
                }}
            ],
            "moneda": "PEN/USD",
            "metadatos": {{
                "calidad_imagen": "alta/media/baja",
                "texto_legible": true/false,
                "campos_faltantes": ["lista de campos que no se pudieron leer"]
            }}
        }}
        
        IMPORTANTE:
        - Para Perú, el IGV es 18%
        - Si es un gasto (compra), tipo = "gasto"
        - Si es un ingreso (venta), tipo = "ingreso"
        - Sé preciso con los montos
        - Si algo no está claro, indica baja confianza
        
        Devuelve SOLO el JSON, sin texto adicional.
        """
    
    def _crear_prompt_excel(self, empresa: Empresa, excel_text: str) -> str:
        """Crea prompt para procesar Excel"""
        return f"""
        Analiza este archivo Excel de transacciones para "{empresa.nombre}":
        
        {excel_text}
        
        Normaliza y estructura los datos en JSON:
        
        {{
            "transacciones": [
                {{
                    "fecha": "YYYY-MM-DD",
                    "tipo": "ingreso" o "gasto",
                    "monto": número decimal,
                    "descripcion": "descripción",
                    "categoria_sugerida": "categoría",
                    "metodo_pago_sugerido": "método",
                    "numero_comprobante": "si existe",
                    "confianza": 0-100,
                    "fila_origen": número de fila
                }}
            ],
            "resumen": {{
                "total_registros": número,
                "registros_validos": número,
                "registros_con_errores": número,
                "errores": ["lista de errores encontrados"]
            }}
        }}
        
            Devuelve SOLO el JSON.
        """
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parsea respuesta JSON de Gemini (puede venir con markdown)"""
        try:
            # Limpiar markdown si existe
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Parsear JSON
            return json.loads(response_text.strip())
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Error al parsear respuesta de IA: {str(e)}")
    
    def _validar_y_enriquecer(self, resultado: Dict, empresa: Empresa) -> Dict:
        """Valida y enriquece los datos extraídos"""
        # Validar que existan transacciones
        if 'transacciones' not in resultado:
            resultado['transacciones'] = []
        
        # Enriquecer cada transacción
        for trans in resultado['transacciones']:
            # Asegurar que tenga todos los campos
            trans.setdefault('tipo', 'ingreso')
            trans.setdefault('confianza', 50.0)
            trans.setdefault('descripcion', 'Sin descripción')
            
            # Validar monto
            if isinstance(trans.get('monto'), str):
                trans['monto'] = float(trans['monto'].replace(',', ''))
            
            # Validar categoría (crear si no existe)
            categoria_nombre = trans.get('categoria_sugerida', 'Otros')
            if not CategoriaTransaccion.objects.filter(nombre=categoria_nombre).exists():
                trans['categoria_nueva'] = True
            
            # Validar método de pago
            metodo_nombre = trans.get('metodo_pago_sugerido', 'Efectivo')
            if not MetodoPago.objects.filter(nombre=metodo_nombre).exists():
                trans['metodo_nuevo'] = True
        
        # Añadir metadatos de procesamiento
        resultado['procesado_con'] = 'OpenAI GPT-4o'
        resultado['timestamp'] = datetime.now().isoformat()
        resultado['empresa_id'] = empresa.id
        
        return resultado
    
    def _dataframe_to_structured_text(self, df) -> str:
        """Convierte DataFrame a texto estructurado para IA"""
        import pandas as pd
        
        # Obtener info del DataFrame
        info = f"Columnas: {list(df.columns)}\n"
        info += f"Filas: {len(df)}\n\n"
        
        # Primeras 20 filas en formato tabla
        info += "Datos (primeras 20 filas):\n"
        info += df.head(20).to_string()
        
        return info
