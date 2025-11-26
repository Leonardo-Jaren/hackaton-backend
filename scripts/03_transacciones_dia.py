import requests
import os
import random
from datetime import date, datetime, timedelta

BASE_URL = os.environ.get('BASE_URL')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
USUARIO_ID = os.environ.get('USUARIO_ID')
HEADERS = {'Authorization': f'Token {AUTH_TOKEN}'}

# IDs de Categorías y Métodos (Asumimos que el setup las creó con IDs 1 a N)
# DEBES REVISAR TUS IDs reales si la base de datos no está limpia.
CATEGORIAS_INGRESOS = [1, 2, 3] # Producto A, Artesanía, Delivery
CATEGORIAS_EGRESOS = [4, 5, 6, 7] # Alquiler, Insumos, Servicios, Movilidad
METODOS_PAGO_IDS = [1, 2, 3, 4] # Efectivo, Tarjeta, Yape/Plin, Transferencia

def generate_random_transactions(num_transactions=25):
    transactions_added = 0
    print(f"   -> Generando {num_transactions} transacciones de prueba...")

    for i in range(num_transactions):
        # 80% de probabilidad de ser INGRESO (Venta), 20% de EGRESO (Gasto)
        is_ingreso = random.random() < 0.8
        
        if is_ingreso:
            monto = round(random.uniform(5.0, 80.0), 2)  # Ventas entre S/ 5 y S/ 80
            categoria_id = random.choice(CATEGORIAS_INGRESOS)
            metodo_id = random.choice([1, 2, 3]) # Mayormente efectivo, tarjeta o Yape
            tipo = "INGRESO"
            descripcion = f"Venta aleatoria #{i+1}"
        else:
            monto = round(random.uniform(10.0, 150.0), 2) # Gastos entre S/ 10 y S/ 150
            categoria_id = random.choice(CATEGORIAS_EGRESOS)
            metodo_id = random.choice([1, 4]) # Mayormente Efectivo o Transferencia
            tipo = "EGRESO"
            descripcion = f"Gasto operativo #{i+1}"

        # Simular una hora del día
        hora_simulada = (datetime.now() - timedelta(hours=random.randint(1, 8), minutes=random.randint(1, 59))).time()
        
        data = {
            "tipo": tipo,
            "monto": monto,
            "categoria": categoria_id,
            "metodo_pago": metodo_id,
            "descripcion": descripcion,
            "cajero": USUARIO_ID,
            "fecha": str(date.today()), # Django puede requerir la fecha aquí
            "hora": str(hora_simulada)
        }

        response = requests.post(f"{BASE_URL}/transacciones/registro/", json=data, headers=HEADERS)
        
        if response.status_code == 201:
            transactions_added += 1
        # else: print(f"      [ERROR] Transacción fallida {i+1}: {response.text}")

    print(f"      [OK] Total de {transactions_added} transacciones insertadas.")

if __name__ == "__main__":
    generate_random_transactions()