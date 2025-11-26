from django.db import models

# Create your models here.
class Empresa(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Empresa')
    ruc = models.CharField(max_length=11, unique=True, verbose_name='RUC')
    direccion = models.CharField(max_length=200, verbose_name='Dirección')
    regimen_tributario = models.CharField(max_length=100, verbose_name='Régimen Tributario')

    def __str__(self):
        return self.nombre
    
class CategoriaTransaccion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Categoría')
    tipo = models.CharField(max_length=50, choices=[('ingreso', 'Ingreso'), ('gasto', 'Egreso')], verbose_name='Tipo de Categoría')

    def __str__(self):
        return self.nombre
    
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Método de Pago')

    def __str__(self):
        return self.nombre