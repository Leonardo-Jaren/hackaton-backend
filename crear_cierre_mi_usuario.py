import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from cierre_caja.services.cierre_caja_service import CierreCajaService
from transacciones.models import FondoCaja
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

# Obtener el usuario marcelepwi@gmail.com
user = User.objects.get(email='marcelepwi@gmail.com')

print(f'👤 Usuario: {user.email}')
print(f'🏢 Empresa: {user.empresa.nombre if user.empresa else "Sin empresa"}')
print()

# Crear un fondo de caja para este usuario si no existe
from transacciones.models import FondoCaja
from datetime import date

hoy = date.today()
fondo = FondoCaja.objects.filter(
    empresa=user.empresa,
    creado_por=user,
    fecha=hoy
).first()

if not fondo:
    print('📦 Creando fondo de caja...')
    fondo = FondoCaja.objects.create(
        empresa=user.empresa,
        monto=Decimal('500.00'),
        creado_por=user,
        observaciones='Fondo de prueba para cierre de caja'
    )
    print(f'✅ Fondo creado: S/ {fondo.monto}')
else:
    print(f'📦 Fondo existente: S/ {fondo.monto}')

print()

# Crear cierre de caja
service = CierreCajaService()

try:
    resultado = service.iniciar_cierre(
        fondo_caja_id=fondo.id,
        usuario_id=user.id
    )
    
    print('✅ Cierre de caja creado exitosamente!')
    print(f'   ID: {resultado["cierre_id"]}')
    print(f'   Estado: {resultado["estado"]}')
    print(f'   Fondo Inicial: S/ {resultado["fondo_inicial"]}')
    print()
    print(f'🎯 Usa el cierre ID {resultado["cierre_id"]} en el frontend')
    
except ValueError as e:
    if 'Ya existe un cierre abierto' in str(e):
        # Buscar el cierre existente
        from cierre_caja.models import CierreCaja
        cierre = CierreCaja.objects.filter(cajero=user, estado='abierto').first()
        if cierre:
            print(f'⚠️ Ya existe un cierre abierto')
            print(f'   ID: {cierre.id}')
            print(f'   Estado: {cierre.estado}')
            print()
            print(f'🎯 Usa el cierre ID {cierre.id} en el frontend')
    else:
        print(f'❌ Error: {e}')
except Exception as e:
    print(f'❌ Error creando cierre: {e}')
    import traceback
    traceback.print_exc()
