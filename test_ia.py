"""
Script de prueba para las funciones de IA con OpenAI
"""
import os
import django
import sys

# Configurar Django
sys.path.append('/home/mightycough/HACKATON-2025/hackaton-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from transacciones.services.gemini_service import GeminiService
from transacciones.models import Empresa, CategoriaTransaccion, MetodoPago
from decimal import Decimal
from datetime import date

def crear_datos_base():
    """Crear datos base para las pruebas"""
    print("📦 Creando datos base...")
    
    # Crear empresa si no existe
    empresa, created = Empresa.objects.get_or_create(
        ruc='20123456789',
        defaults={
            'nombre': 'Mi Empresa Test S.A.C.',
            'direccion': 'Av. Prueba 123, Lima',
            'regimen_tributario': 'Régimen General'
        }
    )
    if created:
        print(f"  ✅ Empresa creada: {empresa.nombre}")
    else:
        print(f"  ℹ️  Empresa existente: {empresa.nombre}")
    
    # Crear categorías si no existen
    categorias = [
        ('Ventas', 'ingreso'),
        ('Servicios', 'ingreso'),
        ('Alquiler', 'gasto'),
        ('Servicios Básicos', 'gasto'),
        ('Compras', 'gasto'),
    ]
    
    for nombre, tipo in categorias:
        cat, created = CategoriaTransaccion.objects.get_or_create(
            nombre=nombre,
            defaults={'tipo': tipo}
        )
        if created:
            print(f"  ✅ Categoría creada: {nombre} ({tipo})")
    
    # Crear métodos de pago si no existen
    metodos = ['Efectivo', 'Transferencia', 'Tarjeta', 'Yape', 'Plin']
    for nombre in metodos:
        met, created = MetodoPago.objects.get_or_create(nombre=nombre)
        if created:
            print(f"  ✅ Método de pago creado: {nombre}")
    
    return empresa


def test_clasificar_transaccion(service, empresa):
    """Test 1: Clasificar una transacción automáticamente"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Clasificar Transacción")
    print("="*60)
    
    casos = [
        ("Pago de luz del mes de enero", 120.50),
        ("Venta de productos varios", 350.00),
        ("Recarga de tóner para impresora", 85.00),
        ("Pago de alquiler local comercial", 1500.00),
    ]
    
    for descripcion, monto in casos:
        print(f"\n📝 Descripción: {descripcion}")
        print(f"💰 Monto: S/ {monto}")
        
        try:
            resultado = service.clasificar_transaccion(
                descripcion=descripcion,
                monto=monto,
                empresa=empresa
            )
            
            print(f"  ✅ Tipo: {resultado.get('tipo', 'N/A')}")
            print(f"  ✅ Categoría sugerida: {resultado.get('categoria_sugerida', 'N/A')}")
            print(f"  ✅ Método de pago: {resultado.get('metodo_pago_sugerido', 'N/A')}")
            print(f"  ✅ Confianza: {resultado.get('confianza', 0)}%")
            if resultado.get('razon'):
                print(f"  ℹ️  Razón: {resultado['razon']}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")


def test_validar_transaccion(service, empresa):
    """Test 2: Validar y corregir una transacción"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Validar y Corregir Transacción")
    print("="*60)
    
    transaccion_data = {
        'descripcion': 'pago luz',  # Descripción pobre
        'monto': 'ciento veinte',   # Monto como texto
        'tipo': 'egreso',
        'categoria': 'Servicios',
        'metodo_pago': 'efectivo'
    }
    
    print(f"\n📋 Datos originales:")
    for key, value in transaccion_data.items():
        print(f"  {key}: {value}")
    
    try:
        resultado = service.validar_y_corregir_transaccion(
            transaccion_data=transaccion_data,
            empresa=empresa
        )
        
        print(f"\n✨ Resultado de validación:")
        print(f"  ✅ Es válida: {resultado.get('es_valida', False)}")
        
        if resultado.get('errores'):
            print(f"\n❌ Errores encontrados:")
            for error in resultado['errores']:
                print(f"  - {error}")
        
        if resultado.get('correcciones_sugeridas'):
            print(f"\n📝 Correcciones sugeridas:")
            for key, value in resultado['correcciones_sugeridas'].items():
                print(f"  {key}: {value}")
        
        if resultado.get('alertas'):
            print(f"\n⚠️  Alertas:")
            for alerta in resultado['alertas']:
                print(f"  - {alerta}")
                
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")


def test_detectar_duplicados(service, empresa):
    """Test 3: Detectar transacciones duplicadas"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Detectar Duplicados")
    print("="*60)
    
    transaccion_nueva = {
        'descripcion': 'Pago de alquiler local comercial',
        'monto': 1500.00,
        'fecha': str(date.today()),
        'tipo': 'egreso'
    }
    
    transacciones_existentes = [
        {
            'descripcion': 'Alquiler del local',
            'monto': 1500.00,
            'fecha': str(date.today()),
            'tipo': 'egreso'
        },
        {
            'descripcion': 'Pago de luz',
            'monto': 120.00,
            'fecha': str(date.today()),
            'tipo': 'egreso'
        }
    ]
    
    print(f"\n📋 Nueva transacción:")
    for key, value in transaccion_nueva.items():
        print(f"  {key}: {value}")
    
    print(f"\n📚 Transacciones existentes: {len(transacciones_existentes)}")
    
    try:
        resultado = service.detectar_duplicados(
            transaccion_nueva=transaccion_nueva,
            transacciones_existentes=transacciones_existentes
        )
        
        print(f"\n✨ Resultado:")
        print(f"  {'🔴' if resultado.get('es_duplicado', False) else '🟢'} Es duplicado: {resultado.get('es_duplicado', False)}")
        print(f"  📊 Probabilidad: {resultado.get('probabilidad_duplicado', 0)}%")
        print(f"  💡 Recomendación: {resultado.get('recomendacion', 'N/A')}")
        
        if resultado.get('duplicados_potenciales'):
            print(f"\n⚠️  Duplicados potenciales encontrados:")
            for dup in resultado['duplicados_potenciales']:
                print(f"  - Índice {dup.get('indice')}: {dup.get('similitud')}% - {dup.get('razon')}")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")


def test_sugerir_categorias(service, empresa):
    """Test 4: Sugerir nuevas categorías basadas en uso"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Sugerir Nuevas Categorías")
    print("="*60)
    
    transacciones_recientes = [
        {'descripcion': 'Compra de útiles de oficina', 'monto': 50, 'tipo': 'gasto'},
        {'descripcion': 'Pago de hosting web', 'monto': 120, 'tipo': 'gasto'},
        {'descripcion': 'Renovación de dominio', 'monto': 80, 'tipo': 'gasto'},
        {'descripcion': 'Publicidad en Facebook', 'monto': 200, 'tipo': 'gasto'},
        {'descripcion': 'Mantenimiento de equipos', 'monto': 300, 'tipo': 'gasto'},
    ]
    
    print(f"\n📋 Transacciones recientes: {len(transacciones_recientes)}")
    for i, trans in enumerate(transacciones_recientes, 1):
        print(f"  {i}. {trans['descripcion']} - S/ {trans['monto']}")
    
    try:
        categorias_sugeridas = service.sugerir_categorias_faltantes(
            empresa=empresa,
            transacciones_recientes=transacciones_recientes
        )
        
        if categorias_sugeridas:
            print(f"\n✨ Nuevas categorías sugeridas:")
            for cat in categorias_sugeridas:
                print(f"  ✅ {cat.get('nombre')} ({cat.get('tipo')})")
                print(f"     📝 Descripción: {cat.get('descripcion', 'N/A')}")
                print(f"     🎯 Prioridad: {cat.get('prioridad', 'N/A')}")
                if cat.get('ejemplos'):
                    print(f"     💡 Ejemplos: {', '.join(cat['ejemplos'][:2])}")
        else:
            print(f"\n  ℹ️  No se sugirieron nuevas categorías")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")


def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de IA con OpenAI GPT-4o")
    print("="*60)
    
    # Verificar API key
    from django.conf import settings
    if not settings.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY no está configurada en .env")
        return
    
    print(f"✅ API Key configurada: {settings.OPENAI_API_KEY[:20]}...")
    
    # Crear datos base
    empresa = crear_datos_base()
    
    # Inicializar servicio
    print("\n🔧 Inicializando GeminiService (ahora con OpenAI)...")
    service = GeminiService()
    print("✅ Servicio inicializado correctamente")
    
    # Ejecutar tests
    try:
        test_clasificar_transaccion(service, empresa)
        test_validar_transaccion(service, empresa)
        test_detectar_duplicados(service, empresa)
        test_sugerir_categorias(service, empresa)
        
        print("\n" + "="*60)
        print("✅ ¡Todas las pruebas completadas!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
