from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('', include('users.urls')),
    path('', include('cierre_caja.urls.cierre_caja_urls')),
    path('', include('core.urls.core_urls')),
    path('', include('transacciones.urls')),
]