from users.repositories.user_repo import UserRepository
from users.repositories.otp_repo import OTPRepository
from users.utils.email_utils import send_mail
from users.interface.auth_backend import GoogleAuthBackend
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """
    Servicio de Autenticación. Maneja el registro, login y la gestión de tokens/OTP.
    """
    def __init__(self, user_repo: UserRepository = None, otp_repo: OTPRepository = None):
        # Inyección de dependencia del repositorio para pruebas unitarias
        self.user_repo = user_repo or UserRepository()
        self.otp_repo = otp_repo or OTPRepository()
        
    def send_verification_otp(self, email: str) -> None:
        """
        Busca al usuario, crea un nuevo OTP y lo envía por correo electrónico.
        """
        # 1. Buscar al usuario
        user = self.user_repo.get_by_email(email)
        
        if user is None:
            # Por seguridad, retornamos sin informar si el email existe.
            logger.warning(f"Intento de OTP para email no registrado: {email}")
            return 
        
        # 2. Crear y guardar el OTP en la base de datos
        otp_instance = self.otp_repo.create_otp(user)
        
        # 3. Enviar el código por correo electrónico
        subject = 'Tu Código de Verificación de Cuenta'
        body = (f'Hola {user.get_full_name() or user.email},\n\n'
                f'Tu código de verificación de un solo uso (OTP) es: '
                f'**{otp_instance.otp_code}**\n\n'
                f'Este código expirará en 15 minutos. No lo compartas.\n\n'
                f'Si no solicitaste este código, puedes ignorar este correo.')
        
        send_mail(
            subject=subject,
            message=body,
            recipient_list=[user.email]
        )
      
    def validate_otp(self, email: str, otp_code: str) -> CustomUser:
        """
        Valida el OTP y retorna el usuario si es correcto.
        Lanza una excepción si no es válido (ValueError).
        """
        user = self.user_repo.get_by_email(email)
        
        if user is None:
            # Error genérico por seguridad
            raise ValueError("Código OTP inválido o expirado.") 
        
        # 1. Obtener el OTP válido y no usado (el repo también comprueba la expiración)
        otp_instance = self.otp_repo.get_valid_otp(user, otp_code)
        
        if otp_instance is None:
            raise ValueError("Código OTP inválido o expirado.")

        # 2. Marcar el OTP como usado
        self.otp_repo.mark_as_used(otp_instance)
        
        return user
      
    # --- Lógica de Registro ---
    def register_user(self, email, password, rol='cajero', empresa_id=None, first_name='', last_name=''):
        """Registra un nuevo usuario con correo/contraseña."""
        if self.user_repo.get_by_email(email):
            raise ValueError("El correo ya está registrado.")
        
        user_data = {
            'email': email,
            'password': password,
            'rol': rol,
            'first_name': first_name,
            'last_name': last_name,
        }
        
        # Agregar empresa_id si se proporciona
        if empresa_id:
            user_data['empresa_id'] = empresa_id
        
        user = self.user_repo.create_user_with_password(**user_data)
        # Aquí se podría generar y enviar el primer OTP para verificar el email.
        return user

    # --- Lógica de Registro Social ---
    def register_or_login_google(self, token: str, rol='cajero', empresa_id=None):
        """
        Valida el token de Google y registra/autentica al usuario.
        Retorna (usuario, es_nuevo).
        """
        google_data = GoogleAuthBackend.validate_token(token)
        
        if not google_data:
            raise ValueError("Token de Google inválido o expirado.")
        
        logger.info(f"Datos de Google recibidos: {google_data}")
            
        email = google_data['email']
        user = self.user_repo.get_by_email(email)
        is_new = False
        
        if user is None:
            # El usuario no existe, lo creamos
            user_data = {
                'email': email,
                'first_name': google_data.get('first_name'),
                'last_name': google_data.get('last_name'),
                'avatar_url': google_data.get('avatar_url'),
                'rol': rol,
            }
            
            if empresa_id:
                user_data['empresa_id'] = empresa_id
                
            user = self.user_repo.create_social_user(**user_data)
            is_new = True
            logger.info(f"Nuevo usuario creado: {email}")
        else:
            # Si el usuario existe, se actualiza el nombre y avatar
            self.user_repo.update(user, 
                first_name=google_data.get('first_name'),
                last_name=google_data.get('last_name'),
                avatar_url=google_data.get('avatar_url')
            )
            logger.info(f"Usuario actualizado: {email}")

        return user, is_new

    # --- Lógica de Login y Tokens ---
    def login_user(self, email, password):
        """Autentica un usuario y genera tokens JWT."""
        # Django por defecto espera 'username', pero nosotros usamos el email como username
        user = authenticate(username=email, password=password)
        
        if user is None:
            # Permite el login social si no hay contraseña
            if password is None:
                user = self.user_repo.get_by_email(email)
            
            # Si el usuario sigue siendo None (auth fallida o usuario no encontrado)
            if user is None:
                raise ValueError("Credenciales inválidas.")

        # Generar tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }
    
    def reset_password_confirm(self, email: str, otp_code: str, new_password: str) -> None:
        """
        Valida el OTP, marca como usado (si no fue marcado antes) y actualiza la contraseña.
        """
        # 1. Validar el OTP (usa el método que ya tienes)
        # Este método lanzará un ValueError si el OTP es inválido/expirado/usado.
        user = self.validate_otp(email=email, otp_code=otp_code)
                
        # 2. Establecer la nueva contraseña
        # Usamos el método set_password de Django y guardamos.
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        # Nota: El método validate_otp() ya se encarga de llamar a OTPRepository.mark_as_used().
        
    def validate_otp(self, email: str, otp_code: str) -> CustomUser:
        """
        Valida el OTP y retorna el usuario si es correcto.
        Lanza una excepción si no es válido (ValueError).
        """
        user = self.user_repo.get_by_email(email)
        
        if user is None:
            # Error genérico por seguridad
            raise ValueError("Código OTP inválido o expirado.") 
        
        # 1. Obtener el OTP válido y no usado (el repo también comprueba la expiración)
        otp_instance = self.otp_repo.get_valid_otp(user, otp_code)
        
        if otp_instance is None:
            raise ValueError("Código OTP inválido o expirado.")

        # 2. Marcar el OTP como usado
        self.otp_repo.mark_as_used(otp_instance)
        
        return user