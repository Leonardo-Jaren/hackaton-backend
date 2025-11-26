from django.urls import path
from users.views.user_views import (
    UserProfileView,
    UsersByEmpresaView,
    UsersByRolView,
    UpdateUserRolView
)

urlpatterns = [
    # Perfil de usuario
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Usuarios por empresa
    path('empresa/<int:empresa_id>/', UsersByEmpresaView.as_view(), name='users_by_empresa'),
    
    # Usuarios por rol
    path('rol/', UsersByRolView.as_view(), name='users_by_rol'),
    
    # Actualizar rol de usuario
    path('<int:user_id>/rol/', UpdateUserRolView.as_view(), name='update_user_rol'),
]
