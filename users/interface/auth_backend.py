from django.conf import settings
from users.models import CustomUser
import requests
import logging

logger = logging.getLogger(__name__)

class GoogleAuthBackend:
    """
    Clase que maneja la validación del token de Google.
    
    Siguiendo el principio de Abierto/Cerrado (OCP), si mañana cambias a Facebook
    o Apple, solo necesitas crear una nueva clase (e.g., AppleAuthBackend)
    que implemente una lógica similar sin tocar el servicio de registro.
    """
    
    @staticmethod
    def validate_token(token: str) -> dict | None:
        """
        Valida el token de Google (Access Token o ID Token) y retorna los datos del usuario.
        """
        try:
            # Intentar primero como access_token (más común con OAuth2)
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Datos recibidos de Google API (userinfo): {data}")
                
                # Validar que el email esté verificado
                if not data.get('verified_email'):
                    logger.warning("Email no verificado en Google")
                    return None
                
                result = {
                    'email': data.get('email'),
                    'first_name': data.get('given_name'),
                    'last_name': data.get('family_name'),
                    'avatar_url': data.get('picture'),
                }
                logger.info(f"Datos procesados para retornar: {result}")
                return result
            
            # Si falla, intentar como id_token
            response = requests.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Datos recibidos de Google API (tokeninfo): {data}")
            
            if data.get('aud') != settings.GOOGLE_CLIENT_ID:
                # Validar que el token está destinado a tu aplicación (audiencia)
                logger.warning("Token no destinado a esta aplicación")
                return None 

            if data.get('email_verified') != 'true':
                logger.warning("Email no verificado en tokeninfo")
                return None

            result = {
                'email': data.get('email'),
                'first_name': data.get('given_name'),
                'last_name': data.get('family_name'),
                'avatar_url': data.get('picture'),
            }
            logger.info(f"Datos procesados para retornar (tokeninfo): {result}")
            return result
        
        except requests.RequestException as e:
            # Loguear el error de conexión
            logger.error(f"Error al validar token de Google: {e}")
            return None