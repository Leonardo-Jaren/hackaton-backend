from django.db.models import Model

class BaseRepository:
    """Clase base para operaciones comunes de repositorio."""
    model: Model = None # Debe ser sobreescrito por la clase hija

    def get_by_id(self, pk):
        """Obtiene un objeto por su clave primaria."""
        return self.model.objects.filter(pk=pk).first()

    def get_all(self):
        """Obtiene todos los objetos."""
        return self.model.objects.all()

    def create(self, **kwargs):
        """Crea un nuevo objeto."""
        return self.model.objects.create(**kwargs)

    def update(self, instance, **kwargs):
        """Actualiza un objeto existente."""
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save()
        return instance