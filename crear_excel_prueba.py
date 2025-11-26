"""
Script para crear un archivo Excel de prueba para el sistema de transacciones
"""
import pandas as pd
from datetime import date

# Datos de ejemplo
transacciones = [
    {
        'fecha': str(date.today()),
        'tipo': 'ingreso',
        'descripcion': 'Venta de productos varios',
        'monto': 350.00,
        'categoria': 'Ventas',
        'metodo_pago': 'Efectivo'
    },
    {
        'fecha': str(date.today()),
        'tipo': 'egreso',
        'descripcion': 'Pago de luz del mes',
        'monto': 120.50,
        'categoria': 'Servicios Básicos',
        'metodo_pago': 'Transferencia'
    },
    {
        'fecha': str(date.today()),
        'tipo': 'ingreso',
        'descripcion': 'Servicio de consultoría',
        'monto': 800.00,
        'categoria': 'Servicios',
        'metodo_pago': 'Transferencia'
    },
    {
        'fecha': str(date.today()),
        'tipo': 'egreso',
        'descripcion': 'Compra de tóner para impresora',
        'monto': 85.00,
        'categoria': 'Compras',
        'metodo_pago': 'Efectivo'
    },
    {
        'fecha': str(date.today()),
        'tipo': 'egreso',
        'descripcion': 'Alquiler del local comercial',
        'monto': 1500.00,
        'categoria': 'Alquiler',
        'metodo_pago': 'Transferencia'
    },
    {
        'fecha': str(date.today()),
        'tipo': 'ingreso',
        'descripcion': 'Venta de servicio técnico',
        'monto': 250.00,
        'categoria': 'Servicios',
        'metodo_pago': 'Yape'
    }
]

# Crear DataFrame
df = pd.DataFrame(transacciones)

# Guardar en Excel
output_file = 'transacciones_prueba.xlsx'
df.to_excel(output_file, index=False, sheet_name='Transacciones')

print(f"✅ Archivo Excel creado: {output_file}")
print(f"📊 Total de transacciones: {len(transacciones)}")
print("\n📋 Contenido:")
print(df.to_string(index=False))
