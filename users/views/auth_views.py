from users.views.base import BaseAPIView
from users.serializers.auth_serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    GoogleAuthSerializer,
    TokenSerializer,
    OTPValidationSerializer,
    OTPRequestSerializer,
    PasswordResetConfirmSerializer,
)
from users.services.auth_service import AuthService
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class RegisterView(BaseAPIView):
    """Vista para el registro de nuevos usuarios."""
    permission_classes = [AllowAny]
    authentication_classes = []  # Evitar error 401 si se envía un token inválido
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                auth_service = AuthService()
                user = auth_service.register_user(
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                
                # Opcional: Iniciar sesión inmediatamente
                tokens = auth_service.login_user(
                    email=user.email, 
                    password=serializer.validated_data['password']
                )

                response_data = TokenSerializer(tokens).data
                
                # --- Seguridad con Cookies (Importante para Vue) ---
                response = Response(response_data, status=status.HTTP_201_CREATED)
                # Configurar cookie para el token de refresco (seguro y persistente)
                response.set_cookie(
                    key='refresh_token',
                    value=tokens['refresh_token'],
                    httponly=True,  # No accesible por JS (CSRF mitigado)
                    secure=True,    # Solo sobre HTTPS (obligatorio en prod)
                    samesite='Lax', # Protección contra ataques CSRF
                    max_age=60 * 60 * 24 * 7 # 7 días
                )
                return response

            except ValueError as e:
                print(f"Register Error (ValueError): {e}")
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except IntegrityError as e:
                print(f"Register Error (IntegrityError): {e}")
                return Response({'detail': 'El correo ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)
        print(f"Register Validation Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(BaseAPIView):
    """Vista para el inicio de sesión tradicional."""
    permission_classes = [AllowAny]
    authentication_classes = []  # Evitar error 401 si se envía un token inválido
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                auth_service = AuthService()
                tokens = auth_service.login_user(
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                
                response_data = TokenSerializer(tokens).data
                response = Response(response_data, status=status.HTTP_200_OK)
                
                # Configurar cookie de refresco
                response.set_cookie(
                    key='refresh_token',
                    value=tokens['refresh_token'],
                    httponly=True, 
                    secure=True, 
                    samesite='Lax',
                    max_age=60 * 60 * 24 * 7
                )
                return response
                
            except ValueError as e:
                return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuthView(BaseAPIView):
    """Vista para el registro/login con token ID de Google."""
    permission_classes = [AllowAny]
    authentication_classes = []  # Evitar error 401 si se envía un token inválido
    
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        if serializer.is_valid():
            try:
                auth_service = AuthService()
                user, is_new = auth_service.register_or_login_google(
                    token=serializer.validated_data['token']
                )

                # Generar tokens JWT para el usuario
                tokens = auth_service.login_user(
                    email=user.email,
                    password=None # Google users don't use password login path
                )
                
                response_data = TokenSerializer(tokens).data
                response = Response(response_data, status=status.HTTP_200_OK)
                
                # Configurar cookie de refresco
                response.set_cookie(
                    key='refresh_token',
                    value=tokens['refresh_token'],
                    httponly=True, 
                    secure=True, 
                    samesite='Lax',
                    max_age=60 * 60 * 24 * 7
                )
                return response
                
            except ValueError as e:
                return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestOTPView(BaseAPIView):
    """
    Vista para solicitar el envío de un código OTP al email del usuario.
    Ruta: /api/auth/otp/request/
    """
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        auth_service = AuthService()
        # El servicio maneja la creación del OTP y el envío del correo
        auth_service.send_verification_otp(email)
        
        # Se retorna HTTP 200/202 por seguridad, sin importar si el email existía.
        return Response(
            {"detail": "Si el email está registrado, se ha enviado un código de verificación."},
            status=status.HTTP_200_OK
        )
        
class OTPValidationView(BaseAPIView):
    """Vista para validar el código OTP."""
    def post(self, request):
        serializer = OTPValidationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                auth_service = AuthService()
                user = auth_service.validate_otp(email=email, otp_code=otp_code)
                
                return Response(
                    {"detail": "Código OTP validado exitosamente."},
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- Vistas para el restablecimiento de contraseña ---
class PasswordResetRequestView(APIView):
    """
    Vista para solicitar el código OTP para restablecer la contraseña.
    """
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data) # Reutilizamos el serializer simple de email
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        auth_service = AuthService()
        # El servicio maneja la creación del OTP y el envío del correo
        auth_service.send_verification_otp(email)
        
        return Response(
            {"detail": "Si el email está registrado, se ha enviado un código de restablecimiento."},
            status=status.HTTP_200_OK
        )

# NOTA: La vista OTPValidationView ya puede servir para validar el código.

class PasswordResetConfirmView(APIView):
    """
    Vista para confirmar la nueva contraseña después de validar el OTP.
    """
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        try:
            auth_service = AuthService()
            auth_service.reset_password_confirm(email, otp_code, new_password)
            
            return Response(
                {"detail": "Contraseña restablecida con éxito. Puedes iniciar sesión."},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            # Captura errores de OTP inválido/expirado
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)