from django.urls import path, include

urlpatterns = [
    path('auth/', include('users.urls.auth_urls')),
    path('users/', include('users.urls.user_urls')),
]

__all__ = ['urlpatterns']