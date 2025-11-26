from django.urls import path
from cierre_caja.views.cierre_caja_views import (
    IniciarCierreView,
    ObtenerResumenCierreView,
    RegistrarEfectivoView,
    FinalizarCierreView,
    DetalleCierreView
)

urlpatterns = [
    # POST /api/cierre_caja/iniciar/ - Iniciar nuevo cierre de caja
    path('iniciar/', IniciarCierreView.as_view(), name='iniciar-cierre'),
    
    # GET /api/cierre_caja/resumen/<int:cierre_id>/ - Obtener resumen del cierre
    path('resumen/<int:cierre_id>/', ObtenerResumenCierreView.as_view(), name='resumen-cierre'),
    
    # PATCH /api/cierre_caja/efectivo/<int:cierre_id>/ - Registrar conteo físico de efectivo
    path('efectivo/<int:cierre_id>/', RegistrarEfectivoView.as_view(), name='registrar-efectivo'),
    
    # POST /api/cierre_caja/finalizar/<int:cierre_id>/ - Finalizar cierre de caja
    path('finalizar/<int:cierre_id>/', FinalizarCierreView.as_view(), name='finalizar-cierre'),
    
    # GET /api/cierre_caja/detalle/<int:cierre_id>/ - Obtener detalle completo del cierre
    path('detalle/<int:cierre_id>/', DetalleCierreView.as_view(), name='detalle-cierre'),
]
