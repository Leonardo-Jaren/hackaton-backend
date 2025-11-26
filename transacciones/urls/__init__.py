from .transaccion_urls import urlpatterns
from django.urls import path, include

urlpatterns = [
    path('transacciones/', include('transacciones.urls.transaccion_urls')),
]

__all__ = ['urlpatterns']