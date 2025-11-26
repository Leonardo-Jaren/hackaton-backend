from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.conf import settings
from users.options import ROL_CHOICES

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    # Elimina el campo username obligatorio
    username = None
    
    # Usa el campo de email como identificador único para el inicio de sesión
    email = models.EmailField(unique=True, verbose_name='email address')
    
    # Deshabilita el campo username obligatorio y lo hace opcional
    user_name = models.CharField(max_length=150, unique=False, blank=True, null=True)
    
    # Campo para la foto de perfil del usuario
    avatar_url = models.URLField(max_length=200, blank=True, null=True)
    
    # Campo de rol del usuario
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cajero', verbose_name='Rol')
    
    # Relación con Empresa
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True, verbose_name='Empresa')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Elimina username de los campos requeridos
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    # Campo adicional
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City / Province')
    # Campo para el titulo o medalla ganada en el juego
    title = models.CharField(max_length=100, default='Novato', verbose_name='Title / Medal')
    
    def __str__(self):
        return f"Profile of {self.user.email}"

# Nuevo modelo para almacenar el código OTP
class OTPVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps', verbose_name="Usuario")
    otp_code = models.CharField(max_length=6, verbose_name="Código OTP")
    created_at = models.DateTimeField(auto_now_add=True)
    # El código expira 15 minutos después de su creación
    expires_at = models.DateTimeField(verbose_name="Fecha de Expiración")
    is_used = models.BooleanField(default=False, verbose_name="¿Usado?")

    class Meta:
        verbose_name = "Verificación OTP"
        verbose_name_plural = "Verificaciones OTP"

    def __str__(self):
        return f"OTP para {self.user.email}: {self.otp_code}"
    
    def is_valid(self):
        """Verifica si el OTP no ha expirado y no ha sido usado."""
        return not self.is_used and self.expires_at > timezone.now()