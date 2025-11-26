import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from cierre_caja.services.cierre_caja_service import CierreCajaService
from transacciones.models import FondoCaja
from django.contrib.auth import get_user_model

User = get_user_model()

# Obtener el primer fondo de caja y su creador
fondo = FondoCaja.objects.select_related('creado_por').first()

if not fondo:
    print('❌ No hay fondos de caja. Ejecuta scripts/run_seed.py primero')
    exit(1)

# Usar el usuario que creó el fondo
user = fondo.creado_por

print(f'📦 Fondo de caja: {fondo.empresa.nombre} - S/ {fondo.monto}')
print(f'👤 Usuario creador: {user.email}')
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
    print(f'   Mensaje: {resultado["mensaje"]}')
    
except Exception as e:
    print(f'❌ Error creando cierre: {e}')
    import traceback
    traceback.print_exc()
