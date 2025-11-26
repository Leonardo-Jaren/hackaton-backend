"""
Script para probar el endpoint de carga de archivos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from transacciones.serializers.transaccion_serializers import ArchivoIAUploadSerializer
from transacciones.services.transaccion_service import TransaccionService

# Probar que el serializer funciona
print("=" * 50)
print("PROBANDO SERIALIZER Y SERVICIO")
print("=" * 50)

try:
    # Verificar que podemos importar y crear el servicio
    service = TransaccionService()
    print("✅ TransaccionService creado exitosamente")
    
    # Verificar que podemos crear el serializer
    data = {
        'empresa': 1,
    }
    
    # Crear un archivo de prueba
    with open('transacciones_prueba.xlsx', 'rb') as f:
        file_content = f.read()
    
    uploaded_file = SimpleUploadedFile(
        name='test.xlsx',
        content=file_content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    data['archivo'] = uploaded_file
    
    serializer = ArchivoIAUploadSerializer(data=data)
    print(f"✅ Serializer creado: {serializer}")
    
    if serializer.is_valid():
        print("✅ Serializer es válido")
        archivo = serializer.save()
        print(f"✅ Archivo guardado: {archivo}")
        
        # Intentar procesar
        print("\n🤖 Procesando con IA...")
        resultado = service.procesar_archivo_ia(archivo.id)
        print(f"✅ Procesamiento exitoso: {resultado}")
        
    else:
        print(f"❌ Errores de validación: {serializer.errors}")
        
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()
