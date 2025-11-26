import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Empresa

User = get_user_model()

# Buscar el usuario
user = User.objects.get(email='marcelepwi@gmail.com')
# Buscar la primera empresa
empresa = Empresa.objects.first()

# Asignar la empresa al usuario
user.empresa = empresa
user.save()

print(f"✅ Usuario {user.email} ahora pertenece a la empresa: {empresa.nombre} (ID: {empresa.id})")
