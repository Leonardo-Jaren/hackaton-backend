from core.repositories.base import BaseRepository
from core.models import CategoriaTransaccion, MetodoPago


class CategoriaTransaccionRepository(BaseRepository):
    """Maneja la persistencia del modelo CategoriaTransaccion."""
    model = CategoriaTransaccion

    def get_by_nombre(self, nombre: str):
        """Obtiene una categoría por su nombre."""
        return self.model.objects.filter(nombre__iexact=nombre).first()

    def get_by_tipo(self, tipo: str):
        """Obtiene todas las categorías de un tipo específico."""
        return self.model.objects.filter(tipo=tipo)

    def create_if_not_exists(self, nombre: str, tipo: str):
        """Crea una categoría solo si no existe."""
        categoria = self.get_by_nombre(nombre)
        if not categoria:
            categoria = self.create(nombre=nombre, tipo=tipo)
        return categoria


class MetodoPagoRepository(BaseRepository):
    """Maneja la persistencia del modelo MetodoPago."""
    model = MetodoPago

    def get_by_nombre(self, nombre: str):
        """Obtiene un método de pago por su nombre."""
        return self.model.objects.filter(nombre__iexact=nombre).first()

    def create_if_not_exists(self, nombre: str):
        """Crea un método de pago solo si no existe."""
        metodo = self.get_by_nombre(nombre)
        if not metodo:
            metodo = self.create(nombre=nombre)
        return metodo
