# users/repositories/otp_repo.py
import uuid
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
# Asume que puedes importar los modelos desde users.models
from users.models import OTPVerification, CustomUser 

class OTPRepository:
    """
    Repositorio para manejar operaciones de base de datos relacionadas
    con OTPVerification.
    """

    @staticmethod
    def create_otp(user: CustomUser, expiration_minutes: int = 15) -> OTPVerification:
        """
        Crea un nuevo código OTP, invalidando cualquier OTP no usado 
        previamente para este usuario.
        """
        # Genera un código de 6 dígitos (usando parte de un UUID para simplicidad)
        otp_code = str(uuid.uuid4().int)[:6] 
        
        # Calcula la fecha de expiración
        expires_at = timezone.now() + timedelta(minutes=expiration_minutes)

        with transaction.atomic():
            # Invalida cualquier OTP no usado previamente (is_used=False -> True)
            OTPVerification.objects.filter(
                user=user, 
                is_used=False
            ).update(is_used=True)

            # Crea y guarda la nueva instancia de OTPVerification
            otp_instance = OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=expires_at
            )
            return otp_instance

    @staticmethod
    def get_valid_otp(user: CustomUser, otp_code: str) -> OTPVerification | None:
        """
        Recupera el OTP más reciente que coincida con el código y el usuario, 
        y que aún no haya sido usado.
        """
        try:
            # Obtiene el OTP más reciente y no usado con el código correcto
            otp_instance = OTPVerification.objects.filter(
                user=user,
                otp_code=otp_code,
                is_used=False
            ).latest('created_at')
            
            # El modelo OTPVerification tiene el método is_valid()
            if otp_instance.is_valid():
                return otp_instance
            else:
                # El código existe pero está expirado.
                return None
        except OTPVerification.DoesNotExist:
            return None

    @staticmethod
    def mark_as_used(otp_instance: OTPVerification) -> None:
        """
        Marca una instancia de OTPVerification como usada.
        """
        otp_instance.is_used = True
        otp_instance.save(update_fields=['is_used'])