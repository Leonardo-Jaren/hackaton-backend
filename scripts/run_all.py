import os
import subprocess
import time

# --- CONFIGURACIÓN ---
BASE_URL = "http://127.0.0.1:8000/api/"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0MTc3OTI4LCJpYXQiOjE3NjQxNzc2MjgsImp0aSI6IjdmOWU3YTEzNTg0NjQ3ZWY5NTgwYzNiZDZlNjMwMzljIiwidXNlcl9pZCI6IjIifQ.UU7lpqXawsNq8E4bWXpJE9d_F0R221ZJIkXZiB--BDk"  # REEMPLAZAR con tu token de un usuario de prueba
USUARIO_ID = 1  # ID del cajero de prueba
EMPRESA_ID = 1  # ID de la microempresa de prueba
# ---------------------

SCRIPTS_TO_RUN = [
    "01_initial_setup.py",
    "02_apertura_fondo.py",
    "03_transacciones_dia.py",
    "04_simular_cierre.py",
]

if __name__ == "__main__":
    print("==============================================")
    print(f"  INICIANDO SIMULACIÓN DE CIERRE DE CAJA EN: {BASE_URL}")
    print("==============================================")

    for script_name in SCRIPTS_TO_RUN:
        print(f"\n---> Ejecutando {script_name}...")
        
        # Ejecutar el script como un subproceso Python
        try:
            # Pasa las variables de configuración como variables de entorno
            env = os.environ.copy()
            env['BASE_URL'] = BASE_URL
            env['AUTH_TOKEN'] = AUTH_TOKEN
            env['USUARIO_ID'] = str(USUARIO_ID)
            env['EMPRESA_ID'] = str(EMPRESA_ID)

            result = subprocess.run(
                ["python", script_name], 
                capture_output=True, 
                text=True, 
                check=True,
                env=env
            )
            print(f"Resultado de {script_name}:\n{result.stdout}")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR al ejecutar {script_name}:")
            print(e.stderr)
            break
        except FileNotFoundError:
            print(f"❌ ERROR: Asegúrate de que '{script_name}' exista en la carpeta.")
            break

    print("\n==============================================")
    print("  SIMULACIÓN FINALIZADA. Verifique su Base de Datos.")
    print("==============================================")