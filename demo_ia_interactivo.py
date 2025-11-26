"""
Demo Interactivo de IA con OpenAI
Prueba las funciones de forma individual
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
from datetime import date
import json


def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print("🤖 DEMO INTERACTIVO - IA CON OPENAI GPT-4o")
    print("="*60)
    print("\n📋 Opciones:")
    print("  1. Clasificar una transacción")
    print("  2. Validar y corregir transacción")
    print("  3. Detectar duplicados")
    print("  4. Sugerir nuevas categorías")
    print("  5. Ver categorías actuales")
    print("  6. Ver métodos de pago")
    print("  0. Salir")
    print("="*60)


def clasificar_demo(service, empresa):
    """Demo de clasificación"""
    print("\n🎯 CLASIFICAR TRANSACCIÓN")
    print("-"*60)
    
    descripcion = input("📝 Descripción de la transacción: ")
    if not descripcion.strip():
        print("❌ Descripción vacía")
        return
    
    try:
        monto = float(input("💰 Monto (S/): "))
    except ValueError:
        print("❌ Monto inválido")
        return
    
    print("\n⏳ Procesando con IA...")
    
    try:
        resultado = service.clasificar_transaccion(
            descripcion=descripcion,
            monto=monto,
            empresa=empresa
        )
        
        print("\n✨ RESULTADO:")
        print("-"*60)
        print(f"  🏷️  Tipo: {resultado.get('tipo', 'N/A').upper()}")
        print(f"  📁 Categoría: {resultado.get('categoria_sugerida', 'N/A')}")
        print(f"  💳 Método de pago: {resultado.get('metodo_pago_sugerido', 'N/A')}")
        print(f"  📊 Confianza: {resultado.get('confianza', 0)}%")
        if resultado.get('razon'):
            print(f"\n  💡 Razón:\n     {resultado['razon']}")
        print("-"*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def validar_demo(service, empresa):
    """Demo de validación"""
    print("\n✅ VALIDAR Y CORREGIR TRANSACCIÓN")
    print("-"*60)
    
    print("\n📋 Ingresa los datos (presiona Enter para valores por defecto):")
    
    descripcion = input("  Descripción: ") or "pago"
    monto = input("  Monto: ") or "100"
    tipo = input("  Tipo (ingreso/egreso): ") or "egreso"
    categoria = input("  Categoría: ") or "Servicios"
    metodo_pago = input("  Método de pago: ") or "efectivo"
    
    transaccion_data = {
        'descripcion': descripcion,
        'monto': monto,
        'tipo': tipo,
        'categoria': categoria,
        'metodo_pago': metodo_pago
    }
    
    print("\n⏳ Validando con IA...")
    
    try:
        resultado = service.validar_y_corregir_transaccion(
            transaccion_data=transaccion_data,
            empresa=empresa
        )
        
        print("\n✨ RESULTADO:")
        print("-"*60)
        print(f"  {'✅' if resultado.get('es_valida') else '❌'} Es válida: {resultado.get('es_valida', False)}")
        print(f"  📊 Confianza: {resultado.get('confianza_validacion', 0)}%")
        
        if resultado.get('errores'):
            print("\n  ❌ ERRORES:")
            for error in resultado['errores']:
                print(f"     • {error}")
        
        if resultado.get('correcciones_sugeridas'):
            print("\n  📝 CORRECCIONES SUGERIDAS:")
            for key, value in resultado['correcciones_sugeridas'].items():
                print(f"     • {key}: {value}")
        
        if resultado.get('alertas'):
            print("\n  ⚠️  ALERTAS:")
            for alerta in resultado['alertas']:
                print(f"     • {alerta}")
        
        print("-"*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def detectar_duplicados_demo(service, empresa):
    """Demo de detección de duplicados"""
    print("\n🔍 DETECTAR DUPLICADOS")
    print("-"*60)
    
    print("\n📝 Nueva transacción:")
    descripcion = input("  Descripción: ") or "Pago de alquiler"
    
    try:
        monto = float(input("  Monto (S/): ") or "1500")
    except ValueError:
        print("❌ Monto inválido")
        return
    
    transaccion_nueva = {
        'descripcion': descripcion,
        'monto': monto,
        'fecha': str(date.today()),
        'tipo': 'egreso'
    }
    
    # Simular transacciones existentes
    transacciones_existentes = [
        {
            'descripcion': 'Alquiler del local',
            'monto': 1500.0,
            'fecha': str(date.today()),
            'tipo': 'egreso'
        },
        {
            'descripcion': 'Pago de luz',
            'monto': 120.0,
            'fecha': str(date.today()),
            'tipo': 'egreso'
        },
        {
            'descripcion': 'Compra de insumos',
            'monto': 350.0,
            'fecha': str(date.today()),
            'tipo': 'egreso'
        }
    ]
    
    print(f"\n⏳ Comparando con {len(transacciones_existentes)} transacciones existentes...")
    
    try:
        resultado = service.detectar_duplicados(
            transaccion_nueva=transaccion_nueva,
            transacciones_existentes=transacciones_existentes
        )
        
        print("\n✨ RESULTADO:")
        print("-"*60)
        print(f"  {'🔴' if resultado.get('es_duplicado') else '🟢'} Es duplicado: {resultado.get('es_duplicado', False)}")
        print(f"  📊 Probabilidad: {resultado.get('probabilidad_duplicado', 0)}%")
        print(f"  💡 Recomendación: {resultado.get('recomendacion', 'N/A').upper()}")
        
        if resultado.get('duplicados_potenciales'):
            print("\n  ⚠️  DUPLICADOS POTENCIALES:")
            for dup in resultado['duplicados_potenciales']:
                idx = dup.get('indice', 0)
                print(f"\n     Transacción #{idx}:")
                print(f"       • Similitud: {dup.get('similitud')}%")
                print(f"       • Razón: {dup.get('razon')}")
                if idx < len(transacciones_existentes):
                    print(f"       • Detalles: {transacciones_existentes[idx]['descripcion']} - S/ {transacciones_existentes[idx]['monto']}")
        
        print("-"*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def ver_categorias():
    """Muestra las categorías actuales"""
    print("\n📁 CATEGORÍAS ACTUALES")
    print("-"*60)
    
    categorias = CategoriaTransaccion.objects.all()
    
    ingresos = categorias.filter(tipo='ingreso')
    gastos = categorias.filter(tipo='gasto')
    
    print("\n💰 INGRESOS:")
    for cat in ingresos:
        print(f"  • {cat.nombre}")
    
    print("\n💸 GASTOS:")
    for cat in gastos:
        print(f"  • {cat.nombre}")
    
    print(f"\nTotal: {categorias.count()} categorías")
    print("-"*60)


def ver_metodos_pago():
    """Muestra los métodos de pago actuales"""
    print("\n💳 MÉTODOS DE PAGO ACTUALES")
    print("-"*60)
    
    metodos = MetodoPago.objects.all()
    
    for metodo in metodos:
        print(f"  • {metodo.nombre}")
    
    print(f"\nTotal: {metodos.count()} métodos")
    print("-"*60)


def main():
    """Función principal"""
    print("\n🚀 Iniciando Demo Interactivo...")
    
    # Verificar API key
    from django.conf import settings
    if not settings.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY no está configurada")
        return
    
    # Obtener empresa
    empresa = Empresa.objects.first()
    if not empresa:
        print("❌ ERROR: No hay empresas registradas")
        return
    
    print(f"✅ Empresa: {empresa.nombre}")
    
    # Inicializar servicio
    service = GeminiService()
    print("✅ Servicio de IA inicializado")
    
    # Loop principal
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n➤ Selecciona una opción: ")
            
            if opcion == '1':
                clasificar_demo(service, empresa)
            elif opcion == '2':
                validar_demo(service, empresa)
            elif opcion == '3':
                detectar_duplicados_demo(service, empresa)
            elif opcion == '4':
                print("\n⚠️  Esta función requiere datos históricos")
                print("   Ejecuta el test completo para ver un ejemplo:")
                print("   python test_ia.py")
            elif opcion == '5':
                ver_categorias()
            elif opcion == '6':
                ver_metodos_pago()
            elif opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("\n❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
