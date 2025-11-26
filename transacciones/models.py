from django.db import models
from django.contrib.auth import get_user_model
from core.models import Empresa, CategoriaTransaccion

User = get_user_model()
    
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Método de Pago')

    def __str__(self):
        return self.nombre

class FondoCaja(models.Model):
    """Fondo inicial de caja para cada día"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto del Fondo')
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación')
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Creado Por')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Fondo de Caja'
        verbose_name_plural = 'Fondos de Caja'
        ordering = ['-fecha']
        unique_together = ['empresa', 'fecha']
    
    def __str__(self):
        return f"Fondo {self.empresa.nombre} - {self.fecha} - S/ {self.monto}"


class Transaccion(models.Model):
    """Registro de transacciones (ingresos/egresos)"""
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Egreso')
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa')
    categoria = models.ForeignKey(CategoriaTransaccion, on_delete=models.PROTECT, verbose_name='Categoría')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, verbose_name='Método de Pago')
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')
    numero_comprobante = models.CharField(max_length=50, blank=True, verbose_name='Número de Comprobante')
    
    # Para relacionar con cierre de caja (futuro)
    cierre_caja = models.ForeignKey(
        'cierre_caja.CierreCaja',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cierre de Caja'
    )
    
    # Para identificar si viene de IA
    procesado_ia = models.BooleanField(default=False, verbose_name='Procesado por IA')
    confianza_ia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Confianza IA (%)'
    )
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tipo.upper()} - S/ {self.monto} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"


class ArchivoIA(models.Model):
    """Archivos subidos para procesamiento de IA"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error')
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa')
    archivo = models.FileField(upload_to='uploads/ia/%Y/%m/%d/', verbose_name='Archivo')
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    resultado_json = models.JSONField(null=True, blank=True, verbose_name='Resultado JSON')
    error_mensaje = models.TextField(blank=True, verbose_name='Mensaje de Error')
    
    class Meta:
        verbose_name = 'Archivo para IA'
        verbose_name_plural = 'Archivos para IA'
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"Archivo {self.id} - {self.estado} - {self.fecha_subida.strftime('%Y-%m-%d %H:%M')}"


class ResultadoIA(models.Model):
    """Resultados individuales del procesamiento de IA"""
    archivo = models.ForeignKey(ArchivoIA, on_delete=models.CASCADE, related_name='resultados', verbose_name='Archivo')
    tipo = models.CharField(max_length=10, choices=[('ingreso', 'Ingreso'), ('gasto', 'Egreso')], verbose_name='Tipo')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    descripcion = models.TextField(verbose_name='Descripción')
    categoria_sugerida = models.CharField(max_length=100, verbose_name='Categoría Sugerida')
    metodo_pago_sugerido = models.CharField(max_length=100, verbose_name='Método de Pago Sugerido')
    confianza = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Confianza (%)')
    numero_comprobante = models.CharField(max_length=50, blank=True, verbose_name='Número de Comprobante')
    
    # Para indicar si ya fue convertido a transacción
    convertido_transaccion = models.BooleanField(default=False, verbose_name='Convertido a Transacción')
    transaccion = models.ForeignKey(
        Transaccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Transacción Asociada'
    )
    
    class Meta:
        verbose_name = 'Resultado IA'
        verbose_name_plural = 'Resultados IA'
        ordering = ['-id']
    
    def __str__(self):
        return f"{self.tipo.upper()} - S/ {self.monto} - Confianza: {self.confianza}%"