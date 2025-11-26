from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class BaseAPIView(APIView):
    """Vista base con autenticación JWT por defecto."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
