from django.db import models

# Create your models here.
class CierreCaja(models.Model):
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Cierre')
    cajero = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='cierres_caja', verbose_name='Cajero')
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='cierres_caja', verbose_name='Empresa')
    fondo_inicial = models.ForeignKey('transacciones.FondoCaja', on_delete=models.CASCADE, related_name='cierres_caja', verbose_name='Fondo de Caja Inicial')
    estado = models.CharField(max_length=50, choices=[('abierto', 'Abierto'), ('cuadrado', 'Cuadrado'), ('descuadrado', 'Descuadrado')], default='abierto', verbose_name='Estado del Cierre de Caja')

    def __str__(self):
        return f'Cierre de Caja {self.id} - {self.cajero.email} - {self.estado}'
    
class ResumenEfectivo(models.Model):
    cierre = models.ForeignKey(CierreCaja, on_delete=models.CASCADE, related_name='resumenes_efectivo', verbose_name='Cierre de Caja')
    efectivo_contado_fisico = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Efectivo Contado Físico')
    ventas_efectivo_sistema = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ventas en Efectivo según Sistema')
    diferencia_efectivo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Diferencia en Efectivo')

    def __str__(self):
        return f'Resumen de Efectivo {self.id} - Cierre {self.cierre.id}'
    
class ResumenMetodoPago(models.Model):
    cierre = models.ForeignKey(CierreCaja, on_delete=models.CASCADE, related_name='resumenes_metodo_pago', verbose_name='Cierre de Caja')
    metodo_pago = models.ForeignKey('core.MetodoPago', on_delete=models.CASCADE, verbose_name='Método de Pago')
    monto_sistema = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total según Sistema')
    monto_banco_o_pos = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total en Banco o POS')
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Diferencia')

    def __str__(self):
        return f'Resumen Método de Pago {self.id} - Cierre {self.cierre.id} - Método {self.metodo_pago.nombre}'
    
class ResultadoCuadre(models.Model):
    cierre = models.ForeignKey(CierreCaja, on_delete=models.CASCADE, related_name='resultados_cuadre', verbose_name='Cierre de Caja')
    es_encuadre_perfecto = models.BooleanField(verbose_name='¿El Cierre está Cuadrado?')
    faltante_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Faltante', default=0)
    sobrante_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Sobrante', default=0)
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones Adicionales')

    def __str__(self):
        return f'Resultado Cuadre {self.id} - Cierre {self.cierre.id}'