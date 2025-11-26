from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('', include('users.urls')),
    path('', include('cierre_caja.urls')),
]