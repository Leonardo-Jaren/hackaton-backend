from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.serializers.auth_serializers import UserDetailSerializer
from users.repositories.user_repo import UserRepository
from users.models import CustomUser


class UserProfileView(APIView):
    """Vista para obtener y actualizar el perfil del usuario autenticado."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtiene el perfil del usuario autenticado."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Actualiza el perfil del usuario autenticado."""
        user = request.user
        user_repo = UserRepository()
        
        # Campos permitidos para actualizar
        allowed_fields = ['first_name', 'last_name', 'avatar_url']
        update_data = {key: value for key, value in request.data.items() if key in allowed_fields}
        
        if update_data:
            user_repo.update(user, **update_data)
        
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersByEmpresaView(APIView):
    """Vista para obtener todos los usuarios de una empresa."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, empresa_id):
        """Obtiene todos los usuarios de una empresa específica."""
        # Verificar que el usuario tenga acceso (opcional: agregar lógica de permisos)
        if request.user.rol != 'administrador' and request.user.empresa_id != empresa_id:
            return Response(
                {'detail': 'No tienes permiso para ver los usuarios de esta empresa.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        usuarios = CustomUser.objects.filter(empresa_id=empresa_id).select_related('empresa')
        serializer = UserDetailSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersByRolView(APIView):
    """Vista para obtener usuarios filtrados por rol."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtiene usuarios filtrados por rol y opcionalmente por empresa."""
        rol = request.query_params.get('rol')
        empresa_id = request.query_params.get('empresa_id')
        
        if not rol:
            return Response(
                {'detail': 'El parámetro "rol" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar permisos
        if request.user.rol != 'administrador':
            return Response(
                {'detail': 'No tienes permiso para realizar esta acción.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = CustomUser.objects.filter(rol=rol).select_related('empresa')
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        serializer = UserDetailSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateUserRolView(APIView):
    """Vista para actualizar el rol de un usuario (solo administradores)."""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, user_id):
        """Actualiza el rol de un usuario específico."""
        # Solo administradores pueden cambiar roles
        if request.user.rol != 'administrador':
            return Response(
                {'detail': 'No tienes permiso para realizar esta acción.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        nuevo_rol = request.data.get('rol')
        if not nuevo_rol or nuevo_rol not in ['administrador', 'cajero']:
            return Response(
                {'detail': 'El rol debe ser "administrador" o "cajero".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = CustomUser.objects.get(id=user_id)
            user_repo = UserRepository()
            user_repo.update(user, rol=nuevo_rol)
            
            serializer = UserDetailSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(
                {'detail': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
