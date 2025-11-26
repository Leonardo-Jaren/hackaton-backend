from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('', include('users.urls')),
    path('', include('cierre_caja.urls')),
    path('', include('core.urls')),
    path('', include('transacciones.urls')),
]