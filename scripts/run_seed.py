"""
Script simplificado para ejecutar el seed_data.py
Ejecutar con: python scripts/run_seed.py
"""
import os
import django
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

# Importar y ejecutar el script de seed
from scripts.seed_data import main

if __name__ == '__main__':
    main()
