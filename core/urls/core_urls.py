from django.urls import path
from core.views.core_views import (
    CrearCategoriaView,
    ListarCategoriasView,
    CrearCategoriasLoteView,
    CrearMetodoPagoView,
    ListarMetodosPagoView,
    CrearMetodosPagoLoteView,
    InicializarDatosView
)


# Vista combinada para manejar GET y POST de categorías
class CategoriasCombinedView(ListarCategoriasView):
    """Vista que maneja tanto GET (listar) como POST (crear) categorías."""
    
    def post(self, request):
        """Delega al view de creación."""
        return CrearCategoriaView().post(request)


# Vista combinada para manejar GET y POST de métodos de pago
class MetodosPagoCombinedView(ListarMetodosPagoView):
    """Vista que maneja tanto GET (listar) como POST (crear) métodos de pago."""
    
    def post(self, request):
        """Delega al view de creación."""
        return CrearMetodoPagoView().post(request)


urlpatterns = [
    # --- Categorías de Transacción ---
    # GET/POST /api/core/categorias/ - Listar o crear categoría
    path('categorias/', CategoriasCombinedView.as_view(), name='categorias'),
    
    # POST /api/core/categorias/lote/ - Crear categorías en lote
    path('categorias/lote/', CrearCategoriasLoteView.as_view(), name='crear-categorias-lote'),
    
    # --- Métodos de Pago ---
    # GET/POST /api/core/metodos-pago/ - Listar o crear método de pago
    path('metodos-pago/', MetodosPagoCombinedView.as_view(), name='metodos-pago'),
    
    # POST /api/core/metodos-pago/lote/ - Crear métodos de pago en lote
    path('metodos-pago/lote/', CrearMetodosPagoLoteView.as_view(), name='crear-metodos-pago-lote'),
    
    # --- Inicialización ---
    # POST /api/core/inicializar/ - Inicializar datos por defecto
    path('inicializar/', InicializarDatosView.as_view(), name='inicializar-datos'),
]
