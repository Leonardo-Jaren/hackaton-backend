from django.db import models

# Create your models here.
class FondoCaja(models.Model):
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto Inicial')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    cajero = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='fondos_caja', verbose_name='Cajero')

    def __str__(self):
        return f'Fondo de Caja {self.id} - {self.cajero.email} - {self.monto_inicial}'
    
class Transaccion(models.Model):
    tipo = models.CharField(max_length=50, choices=[('ingreso', 'Ingreso'), ('gasto', 'Egreso')], verbose_name='Tipo de Transacción')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    categoria = models.ForeignKey('core.CategoriaTransaccion', on_delete=models.SET_NULL, null=True, verbose_name='Categoría de Transacción')
    metodo_pago = models.ForeignKey('core.MetodoPago', on_delete=models.SET_NULL, null=True, verbose_name='Método de Pago')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    cajero = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='transacciones', verbose_name='Cajero')

    def __str__(self):
        return f'Transacción {self.id} - {self.tipo} - {self.monto}'
    
class CierrePendiente(models.Model):
    archivo_excel = models.FileField(upload_to='cierres_pendientes/excel/', verbose_name='Archivo Excel de Cierre Pendiente')
    imagen_reporte = models.ImageField(upload_to='cierres_pendientes/imagenes/', verbose_name='Imagen de Cierre Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('procesado', 'Procesado')], default='pendiente', verbose_name='Estado del Cierre Pendiente')

    def __str__(self):
        return f'Cierre Pendiente {self.id} - {self.estado}'
    
class ResultadoIA(models.Model):
    transaccion = models.ForeignKey(Transaccion, on_delete=models.CASCADE, related_name='resultados_ia', verbose_name='Transacción')
    data_raw = models.JSONField(verbose_name='Datos Raw Procesados por IA')
    confianza_ia = models.FloatField(verbose_name='Nivel de Confianza de la IA')

    def __str__(self):
        return f'Resultado IA {self.id} - Transacción {self.transaccion.id}'