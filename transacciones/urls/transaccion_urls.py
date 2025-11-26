from django.urls import path
from ..views.transaccion_views import (
    FondoCajaCreateView,
    TransaccionRegistroView,
    TransaccionDetailView,
    CargaDataIAView,
    ResultadosIAView
)

urlpatterns = [
    # Fondo de Caja
    path('fondo-caja/', FondoCajaCreateView.as_view(), name='fondo_caja_create'),
    
    # Transacciones Manuales
    path('registro/', TransaccionRegistroView.as_view(), name='transaccion_registro'),
    path('registro/<int:pk>/', TransaccionDetailView.as_view(), name='transaccion_detail'),
    
    # Procesamiento IA
    path('carga-data/', CargaDataIAView.as_view(), name='carga_data_ia'),
    path('resultados-ia/', ResultadosIAView.as_view(), name='resultados_ia'),
]