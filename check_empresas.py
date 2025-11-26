import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from core.models import Empresa

empresas = Empresa.objects.all()
print(f'\n📊 Total empresas: {empresas.count()}\n')

for e in empresas:
    print(f'  ✅ ID: {e.id}, Nombre: {e.nombre}')

if empresas.count() == 0:
    print('\n⚠️ No hay empresas en la base de datos!')
    print('Necesitas crear al menos una empresa.')
