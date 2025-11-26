import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from cierre_caja.models import CierreCaja

cierres = CierreCaja.objects.all()
print(f'\n📊 Total cierres: {cierres.count()}\n')

for c in cierres:
    print(f'  ID: {c.id}')
    print(f'  Estado: {c.estado}')
    print(f'  Empresa: {c.empresa.nombre}')
    print(f'  Fondo: S/ {c.fondo_caja.monto}')
    print(f'  Creado: {c.fecha_apertura}')
    print()

if cierres.count() == 0:
    print('⚠️ No hay cierres de caja en la base de datos!')
    print('Necesitas crear un cierre primero usando /api/cierre_caja/iniciar/')
