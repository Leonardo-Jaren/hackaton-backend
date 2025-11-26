from users.repositories.base import BaseRepository
from users.models import CustomUser

class UserRepository(BaseRepository):
    """Maneja la persistencia del modelo CustomUser."""
    model = CustomUser

    def get_by_email(self, email: str) -> CustomUser | None:
        """
        Obtiene un usuario por su correo electrónico, usando una consulta 
        insensible a mayúsculas y minúsculas (iexact).
        """
        return self.model.objects.filter(email__iexact=email).first()

    def create_user_with_password(self, email, password, **extra_fields) -> CustomUser:
        """Crea un usuario con contraseña (Registro tradicional)."""
        # Utiliza el método nativo de Django para hashear la contraseña
        return self.model.objects.create_user(email=email, password=password, **extra_fields)
    
    def create_social_user(self, email, **extra_fields) -> CustomUser:
        """Crea un usuario social (sin contraseña)."""
        # Usa el método create_user pero sin pasar la contraseña
        return self.model.objects.create_user(email=email, password=None, **extra_fields)