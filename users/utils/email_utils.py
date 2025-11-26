# users/utils/email_utils.py
import logging
from django.conf import settings
import resend

logger = logging.getLogger(__name__)

# Configurar la API key de Resend
API_KEY = getattr(settings, 'RESEND_API_KEY', None)

# Inicialización del cliente
try:
    if API_KEY and API_KEY.startswith('re_') and API_KEY != 'CLAVE_NO_CARGADA':
        resend.api_key = API_KEY
        resend_client = True  # Indicador de que el cliente está configurado
        logger.info("Cliente de Resend configurado correctamente.")
    else:
        logger.error("RESEND_API_KEY está vacía o no es válida. El cliente no se inicializará.")
        resend_client = None
except Exception as e:
    logger.error(f"Error fatal al inicializar el cliente de Resend: {e}")
    resend_client = None

def send_mail(subject: str, message: str, recipient_list: list) -> bool:
    """
    Función de utilidad para enviar correos electrónicos usando la API de Resend.
    """
    if not resend_client:
        logger.error("Cliente de Resend no configurado. No se pudo enviar el correo.")
        return False
        
    try:
        # Llamada a la API
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": recipient_list,
            "subject": subject,
            "text": message, 
        }

        # Usar el módulo resend directamente
        email_response = resend.Emails.send(params)
        
        # La respuesta debe ser exitosa si no hay excepciones
        if email_response and 'id' in email_response:
            logger.info(f"Correo enviado con éxito a {recipient_list}. ID de Resend: {email_response['id']}")
            return True
        else:
            logger.error(f"Fallo al enviar correo a {recipient_list}. Respuesta de Resend: {email_response}")
            return False
        
    except Exception as e:
        logger.error(f"Error al enviar correo a {recipient_list}: {e}")
        return False