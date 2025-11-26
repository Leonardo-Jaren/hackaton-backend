"""
Script para insertar datos de prueba en la base de datos
Ejecutar con: python manage.py shell < scripts/seed_data.py
O dentro de Django shell: exec(open('scripts/seed_data.py').read())
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
    django.setup()

from django.contrib.auth import get_user_model
from core.models import Empresa, CategoriaTransaccion, MetodoPago
from transacciones.models import FondoCaja, Transaccion, MetodoPago as TransaccionMetodoPago

User = get_user_model()

def limpiar_datos():
    """Limpia todos los datos de prueba"""
    print("🗑️  Limpiando datos existentes...")
    Transaccion.objects.all().delete()
    FondoCaja.objects.all().delete()
    CategoriaTransaccion.objects.all().delete()
    MetodoPago.objects.all().delete()
    TransaccionMetodoPago.objects.all().delete()
    Empresa.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print("✅ Datos limpiados\n")

def crear_empresas():
    """Crea empresas de prueba"""
    print("🏢 Creando empresas...")
    empresas = [
        {
            'nombre': 'Bodega San Martin',
            'ruc': '20123456789',
            'direccion': 'Av. Principal 123, Lima',
            'regimen_tributario': 'Régimen MYPE Tributario'
        },
        {
            'nombre': 'Minimarket El Ahorro',
            'ruc': '20987654321',
            'direccion': 'Jr. Los Olivos 456, Callao',
            'regimen_tributario': 'Régimen General'
        },
        {
            'nombre': 'Tienda Don José',
            'ruc': '20555444333',
            'direccion': 'Calle Comercio 789, San Miguel',
            'regimen_tributario': 'Régimen MYPE Tributario'
        }
    ]
    
    empresas_creadas = []
    for emp_data in empresas:
        empresa, created = Empresa.objects.get_or_create(
            ruc=emp_data['ruc'],
            defaults=emp_data
        )
        empresas_creadas.append(empresa)
        status = "✅ Creada" if created else "ℹ️  Ya existía"
        print(f"   {status}: {empresa.nombre}")
    
    print()
    return empresas_creadas

def crear_usuarios(empresas):
    """Crea usuarios de prueba"""
    print("👤 Creando usuarios...")
    usuarios = [
        {
            'email': 'admin@bodega.com',
            'password': 'admin123',
            'rol': 'administrador',
            'empresa': empresas[0],
            'first_name': 'Juan',
            'last_name': 'Pérez'
        },
        {
            'email': 'cajero1@bodega.com',
            'password': 'cajero123',
            'rol': 'cajero',
            'empresa': empresas[0],
            'first_name': 'María',
            'last_name': 'García'
        },
        {
            'email': 'admin@minimarket.com',
            'password': 'admin123',
            'rol': 'administrador',
            'empresa': empresas[1],
            'first_name': 'Carlos',
            'last_name': 'López'
        },
        {
            'email': 'cajero@minimarket.com',
            'password': 'cajero123',
            'rol': 'cajero',
            'empresa': empresas[1],
            'first_name': 'Ana',
            'last_name': 'Martínez'
        }
    ]
    
    usuarios_creados = []
    for user_data in usuarios:
        password = user_data.pop('password')
        email = user_data['email']
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            print(f"   ℹ️  Ya existía: {user.email} ({user.rol})")
        else:
            user = User.objects.create_user(**user_data)
            user.set_password(password)
            user.save()
            print(f"   ✅ Creado: {user.email} ({user.rol}) - Password: {password}")
        
        usuarios_creados.append(user)
    
    print()
    return usuarios_creados

def crear_categorias():
    """Crea categorías de transacciones"""
    print("📂 Creando categorías...")
    categorias = [
        # Categorías de INGRESO
        {'nombre': 'Venta de productos', 'tipo': 'ingreso'},
        {'nombre': 'Servicios prestados', 'tipo': 'ingreso'},
        {'nombre': 'Intereses bancarios', 'tipo': 'ingreso'},
        {'nombre': 'Otros ingresos', 'tipo': 'ingreso'},
        
        # Categorías de EGRESO/GASTO
        {'nombre': 'Compra de mercadería', 'tipo': 'gasto'},
        {'nombre': 'Pago de servicios', 'tipo': 'gasto'},
        {'nombre': 'Sueldos y salarios', 'tipo': 'gasto'},
        {'nombre': 'Alquiler', 'tipo': 'gasto'},
        {'nombre': 'Transporte', 'tipo': 'gasto'},
        {'nombre': 'Mantenimiento', 'tipo': 'gasto'},
        {'nombre': 'Impuestos', 'tipo': 'gasto'},
        {'nombre': 'Otros gastos', 'tipo': 'gasto'},
    ]
    
    categorias_creadas = []
    for cat_data in categorias:
        categoria, created = CategoriaTransaccion.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults=cat_data
        )
        categorias_creadas.append(categoria)
        status = "✅" if created else "ℹ️"
        print(f"   {status} {categoria.nombre} ({categoria.tipo})")
    
    print()
    return categorias_creadas

def crear_metodos_pago():
    """Crea métodos de pago"""
    print("💳 Creando métodos de pago...")
    metodos = ['Efectivo', 'Tarjeta de débito', 'Tarjeta de crédito', 'Yape', 'Plin', 'Transferencia bancaria']
    
    metodos_core = []
    metodos_transaccion = []
    
    for nombre in metodos:
        # Crear en core.MetodoPago
        metodo_core, created1 = MetodoPago.objects.get_or_create(nombre=nombre)
        metodos_core.append(metodo_core)
        
        # Crear en transacciones.MetodoPago
        metodo_trans, created2 = TransaccionMetodoPago.objects.get_or_create(nombre=nombre)
        metodos_transaccion.append(metodo_trans)
        
        status = "✅" if (created1 or created2) else "ℹ️"
        print(f"   {status} {nombre}")
    
    print()
    return metodos_core, metodos_transaccion

def crear_fondos_caja(empresas, usuarios):
    """Crea fondos de caja iniciales"""
    print("💰 Creando fondos de caja...")
    fondos = [
        {'empresa': empresas[0], 'monto': Decimal('500.00'), 'creado_por': usuarios[0], 'observaciones': 'Fondo inicial del día'},
        {'empresa': empresas[1], 'monto': Decimal('1000.00'), 'creado_por': usuarios[2], 'observaciones': 'Fondo inicial del día'},
    ]
    
    fondos_creados = []
    for fondo_data in fondos:
        # Verificar si ya existe un fondo para esa empresa en la fecha de hoy
        empresa = fondo_data['empresa']
        if FondoCaja.objects.filter(empresa=empresa, fecha=datetime.now().date()).exists():
            fondo = FondoCaja.objects.get(empresa=empresa, fecha=datetime.now().date())
            print(f"   ℹ️  Ya existe fondo para {empresa.nombre}: S/ {fondo.monto}")
        else:
            fondo = FondoCaja.objects.create(**fondo_data)
            print(f"   ✅ Creado fondo para {empresa.nombre}: S/ {fondo.monto}")
        
        fondos_creados.append(fondo)
    
    print()
    return fondos_creados

def crear_transacciones(empresas, categorias, metodos_pago):
    """Crea transacciones de prueba"""
    print("💸 Creando transacciones...")
    
    # Obtener categorías por tipo
    cat_ingresos = [c for c in categorias if c.tipo == 'ingreso']
    cat_gastos = [c for c in categorias if c.tipo == 'gasto']
    
    transacciones = [
        # Ingresos de Bodega San Martin
        {
            'empresa': empresas[0],
            'categoria': cat_ingresos[0],  # Venta de productos
            'metodo_pago': metodos_pago[0],  # Efectivo
            'tipo': 'ingreso',
            'monto': Decimal('150.50'),
            'descripcion': 'Venta de abarrotes varios',
            'numero_comprobante': 'B001-00001'
        },
        {
            'empresa': empresas[0],
            'categoria': cat_ingresos[0],
            'metodo_pago': metodos_pago[3],  # Yape
            'tipo': 'ingreso',
            'monto': Decimal('85.00'),
            'descripcion': 'Venta de bebidas y snacks',
            'numero_comprobante': 'B001-00002'
        },
        {
            'empresa': empresas[0],
            'categoria': cat_ingresos[0],
            'metodo_pago': metodos_pago[1],  # Tarjeta de débito
            'tipo': 'ingreso',
            'monto': Decimal('320.75'),
            'descripcion': 'Venta de productos de limpieza',
            'numero_comprobante': 'B001-00003'
        },
        
        # Gastos de Bodega San Martin
        {
            'empresa': empresas[0],
            'categoria': cat_gastos[0],  # Compra de mercadería
            'metodo_pago': metodos_pago[0],  # Efectivo
            'tipo': 'gasto',
            'monto': Decimal('500.00'),
            'descripcion': 'Compra de productos al por mayor',
            'numero_comprobante': 'F001-00123'
        },
        {
            'empresa': empresas[0],
            'categoria': cat_gastos[1],  # Pago de servicios
            'metodo_pago': metodos_pago[5],  # Transferencia
            'tipo': 'gasto',
            'monto': Decimal('80.00'),
            'descripcion': 'Pago de luz del mes',
            'numero_comprobante': 'REC-00456'
        },
        
        # Ingresos de Minimarket El Ahorro
        {
            'empresa': empresas[1],
            'categoria': cat_ingresos[0],
            'metodo_pago': metodos_pago[0],  # Efectivo
            'tipo': 'ingreso',
            'monto': Decimal('450.00'),
            'descripcion': 'Venta del día',
            'numero_comprobante': 'B002-00001'
        },
        {
            'empresa': empresas[1],
            'categoria': cat_ingresos[0],
            'metodo_pago': metodos_pago[2],  # Tarjeta de crédito
            'tipo': 'ingreso',
            'monto': Decimal('280.50'),
            'descripcion': 'Venta de productos premium',
            'numero_comprobante': 'B002-00002'
        },
        
        # Gastos de Minimarket El Ahorro
        {
            'empresa': empresas[1],
            'categoria': cat_gastos[2],  # Sueldos
            'metodo_pago': metodos_pago[5],  # Transferencia
            'tipo': 'gasto',
            'monto': Decimal('1200.00'),
            'descripcion': 'Pago de sueldos',
            'numero_comprobante': 'PLN-001'
        },
        {
            'empresa': empresas[1],
            'categoria': cat_gastos[3],  # Alquiler
            'metodo_pago': metodos_pago[5],  # Transferencia
            'tipo': 'gasto',
            'monto': Decimal('800.00'),
            'descripcion': 'Alquiler del local',
            'numero_comprobante': 'REC-789'
        },
    ]
    
    transacciones_creadas = []
    for i, trans_data in enumerate(transacciones, 1):
        transaccion = Transaccion.objects.create(**trans_data)
        transacciones_creadas.append(transaccion)
        tipo_emoji = "📈" if transaccion.tipo == 'ingreso' else "📉"
        print(f"   {tipo_emoji} {transaccion.empresa.nombre}: {transaccion.tipo.upper()} S/ {transaccion.monto} - {transaccion.descripcion}")
    
    print()
    return transacciones_creadas

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🚀 INICIANDO INSERCIÓN DE DATOS DE PRUEBA")
    print("="*60 + "\n")
    
    try:
        # Limpiar datos existentes (comentar si no se desea)
        # limpiar_datos()
        
        # Crear datos
        empresas = crear_empresas()
        usuarios = crear_usuarios(empresas)
        categorias = crear_categorias()
        metodos_core, metodos_transaccion = crear_metodos_pago()
        fondos = crear_fondos_caja(empresas, usuarios)
        transacciones = crear_transacciones(empresas, categorias, metodos_transaccion)
        
        print("="*60)
        print("✅ DATOS DE PRUEBA INSERTADOS EXITOSAMENTE")
        print("="*60)
        print(f"\n📊 Resumen:")
        print(f"   - Empresas: {len(empresas)}")
        print(f"   - Usuarios: {len(usuarios)}")
        print(f"   - Categorías: {len(categorias)}")
        print(f"   - Métodos de pago: {len(metodos_transaccion)}")
        print(f"   - Fondos de caja: {len(fondos)}")
        print(f"   - Transacciones: {len(transacciones)}")
        print("\n" + "="*60 + "\n")
        
        print("📝 Credenciales de acceso:")
        print("   Admin Bodega San Martin:")
        print("      Email: admin@bodega.com")
        print("      Password: admin123")
        print("\n   Cajero Bodega San Martin:")
        print("      Email: cajero1@bodega.com")
        print("      Password: cajero123")
        print("\n   Admin Minimarket El Ahorro:")
        print("      Email: admin@minimarket.com")
        print("      Password: admin123")
        print("\n   Cajero Minimarket El Ahorro:")
        print("      Email: cajero@minimarket.com")
        print("      Password: cajero123")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error al insertar datos: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
