import requests
import os

BASE_URL = os.environ.get('BASE_URL')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
HEADERS = {'Authorization': f'Token {AUTH_TOKEN}'}

# Datos de prueba realistas para microempresas de Huánuco
CATEGORIAS = [
    {"nombre": "Venta de Producto A (Principal)", "tipo": "INGRESO"},
    {"nombre": "Venta de Artesanía", "tipo": "INGRESO"},
    {"nombre": "Servicio de Delivery", "tipo": "INGRESO"},
    {"nombre": "Pago de Alquiler", "tipo": "EGRESO"},
    {"nombre": "Compra de Insumos/Mercadería", "tipo": "EGRESO"},
    {"nombre": "Pago de Electricidad/Agua", "tipo": "EGRESO"},
    {"nombre": "Gastos de Movilidad Local", "tipo": "EGRESO"},
]

METODOS_PAGO = [
    {"nombre": "Efectivo", "es_efectivo": True},
    {"nombre": "Tarjeta VISA/Mastercard", "es_efectivo": False},
    {"nombre": "Yape/Plin (Transferencia inmediata)", "es_efectivo": False},
    {"nombre": "Transferencia Bancaria", "es_efectivo": False},
]

def create_initial_data():
    # 1. Crear Categorías
    print("   -> Creando categorías...")
    for cat in CATEGORIAS:
        response = requests.post(f"{BASE_URL}/core/categorias/", json=cat, headers=HEADERS)
        if response.status_code in [201, 200]:
            print(f"      [OK] Categoría: {cat['nombre']}")
        else:
            print(f"      [ERROR] Categoría {cat['nombre']}: {response.text}")

    # 2. Crear Métodos de Pago
    print("   -> Creando métodos de pago...")
    for metodo in METODOS_PAGO:
        response = requests.post(f"{BASE_URL}/core/metodos-pago/", json=metodo, headers=HEADERS)
        if response.status_code in [201, 200]:
            print(f"      [OK] Método de Pago: {metodo['nombre']}")
        else:
            print(f"      [ERROR] Método {metodo['nombre']}: {response.text}")

if __name__ == "__main__":
    create_initial_data()