import requests
import os
from datetime import date

BASE_URL = os.environ.get('BASE_URL')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
USUARIO_ID = os.environ.get('USUARIO_ID')
HEADERS = {'Authorization': f'Token {AUTH_TOKEN}'}

def set_fondo_caja():
    # Fondo inicial típico para una microempresa (S/ 150.00)
    FONDO_INICIAL = 150.00 
    
    data = {
        "monto_inicial": FONDO_INICIAL,
        "fecha": str(date.today()),
        "cajero": USUARIO_ID
    }
    
    print(f"   -> Apertura de Caja con S/ {FONDO_INICIAL:.2f}")
    response = requests.post(f"{BASE_URL}/transacciones/fondo-caja/", json=data, headers=HEADERS)
    
    if response.status_code == 201:
        fondo_id = response.json().get('id')
        print(f"      [OK] Fondo de Caja (Apertura) ID: {fondo_id}")
        # Guardar el ID del fondo de caja en el entorno para el cierre posterior
        os.environ['FONDO_CAJA_ID'] = str(fondo_id)
    else:
        print(f"      [ERROR] Apertura fallida: {response.text}")

if __name__ == "__main__":
    set_fondo_caja()