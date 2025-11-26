from django.urls import path, include

urlpatterns = [
    path('cierre_caja/', include('cierre_caja.urls.cierre_caja_urls')),
]

__all__ = ['urlpatterns']