from django.urls import path, include

urlpatterns = [
    path('core/', include('core.urls.core_urls')),
]

__all__ = ['urlpatterns']