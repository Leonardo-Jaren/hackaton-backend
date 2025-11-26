from users.serializers.base import BaseModelSerializer
from rest_framework import serializers
from users.models import CustomUser

# --- Registro Tradicional ---
class UserRegistrationSerializer(serializers.Serializer):
    """Serializer para validar los datos de registro (email y contraseña)."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

# --- Login Tradicional ---
class UserLoginSerializer(serializers.Serializer):
    """Serializer para validar los datos de inicio de sesión."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

# --- Registro Social (Google) ---
class GoogleAuthSerializer(serializers.Serializer):
    """Serializer para recibir el token ID de Google."""
    token = serializers.CharField(required=True)

# --- OTP ---
class OTPRequestSerializer(serializers.Serializer):
    """Serializer para solicitar el envío de un OTP."""
    email = serializers.EmailField(required=True)

class OTPValidationSerializer(serializers.Serializer):
    """Serializer para validar el OTP."""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)

# --- Respuesta (Salida) ---
class UserDetailSerializer(BaseModelSerializer):
    """Serializer para exponer los datos del usuario."""
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'avatar_url')

class TokenSerializer(serializers.Serializer):
    """Serializer para la respuesta con tokens."""
    user = UserDetailSerializer(read_only=True)
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar el cambio de contraseña."""
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        return data