import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("USUARIOS Y SUS EMPRESAS")
print("="*60 + "\n")

users = User.objects.all()

for user in users:
    empresa_info = f"Empresa ID: {user.empresa.id} - {user.empresa.nombre}" if user.empresa else "❌ SIN EMPRESA"
    print(f"📧 {user.email}")
    print(f"   {empresa_info}")
    print(f"   Rol: {user.rol}")
    print()
