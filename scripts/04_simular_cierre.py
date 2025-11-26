import requests
import os
import random

BASE_URL = os.environ.get('BASE_URL')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
USUARIO_ID = os.environ.get('USUARIO_ID')
FONDO_CAJA_ID = os.environ.get('FONDO_CAJA_ID') # Obtenido del paso 2
HEADERS = {'Authorization': f'Token {AUTH_TOKEN}'}

def simulate_cierre():
    # 1. Iniciar el proceso de Cierre de Caja
    print("   -> Iniciando Cierre de Caja...")
    data_inicio = {
        "fondo_inicial": FONDO_CAJA_ID,
        "cajero": USUARIO_ID
    }
    response = requests.post(f"{BASE_URL}/cierre/iniciar/", json=data_inicio, headers=HEADERS)
    if response.status_code != 201:
        print(f"      [ERROR] No se pudo iniciar el cierre: {response.text}")
        return
    
    cierre_id = response.json().get('id')
    print(f"      [OK] Cierre de Caja ID: {cierre_id}")
    
    # 2. Obtener el total de efectivo esperado (Simulación de Resumen)
    response_resumen = requests.get(f"{BASE_URL}/cierre/resumen/{cierre_id}/", headers=HEADERS)
    if response_resumen.status_code != 200:
        print(f"      [ERROR] No se pudo obtener el resumen.")
        return

    # Asumimos que el resumen devuelve el 'total_efectivo_sistema_esperado'
    # Si no tienes un endpoint de resumen, calcula la suma de Fondo + Ingresos Efectivo
    # Para la prueba, usaremos un valor esperado ficticio
    try:
        total_efectivo_esperado = response_resumen.json().get('total_efectivo_sistema_esperado', 500.00) 
    except:
        # Valor de fallback si el endpoint aún no está listo
        total_efectivo_esperado = 500.00 

    # 3. Simular el Conteo Físico
    # Simulación realista: 70% de cuadre, 20% de faltante de S/ 5-10, 10% de sobrante de S/ 1-3
    r = random.random()
    if r < 0.7:
        # Cuadre perfecto o casi perfecto
        conteo_fisico = total_efectivo_esperado
    elif r < 0.9:
        # Faltante (error al dar cambio, gasto no registrado)
        faltante = round(random.uniform(5.0, 10.0), 2)
        conteo_fisico = total_efectivo_esperado - faltante
        print(f"      [ALERTA] Se simula un FALTANTE de S/ {faltante:.2f}")
    else:
        # Sobrante (error al cobrar o registrar de más)
        sobrante = round(random.uniform(1.0, 3.0), 2)
        conteo_fisico = total_efectivo_esperado + sobrante
        print(f"      [ALERTA] Se simula un SOBRANTE de S/ {sobrante:.2f}")

    # 4. Registrar Conteo Físico
    data_conteo = {
        "efectivo_contado_fisico": conteo_fisico,
        "observaciones": "Datos de prueba con simulación de error."
    }
    response_patch = requests.patch(f"{BASE_URL}/cierre/efectivo/{cierre_id}/", json=data_conteo, headers=HEADERS)
    if response_patch.status_code != 200:
        print(f"      [ERROR] No se pudo registrar el conteo: {response_patch.text}")
        return
    print(f"      [OK] Conteo físico (S/ {conteo_fisico:.2f}) registrado.")

    # 5. Finalizar el Cierre
    response_finalizar = requests.post(f"{BASE_URL}/cierre/finalizar/{cierre_id}/", headers=HEADERS)
    if response_finalizar.status_code == 200:
        print(f"      [ÉXITO] Cierre ID {cierre_id} Finalizado con éxito.")
    else:
        print(f"      [ERROR] Error al finalizar el cierre: {response_finalizar.text}")

if __name__ == "__main__":
    simulate_cierre()