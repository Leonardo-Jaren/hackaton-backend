from typing import TypeVar, Generic, List, Optional, Dict, Any
from django.db import models
from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist

# Type variable para el modelo genérico
T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T]):
    """
    Repositorio base genérico para operaciones CRUD
    Proporciona métodos comunes para interactuar con la base de datos
    """
    model: models.Model = None
    
    def __init__(self):
        if self.model is None:
            raise NotImplementedError(
                "Debe especificar el atributo 'model' en la clase hija"
            )
    
    def all(self) -> QuerySet[T]:
        """Obtiene todos los registros del modelo"""
        return self.model.objects.all()
    
    def filter(self, **kwargs) -> QuerySet[T]:
        """
        Filtra registros según los criterios proporcionados
        
        Args:
            **kwargs: Criterios de filtrado
            
        Returns:
            QuerySet con los registros filtrados
            
        Example:
            repo.filter(empresa_id=1, tipo='ingreso')
        """
        return self.model.objects.filter(**kwargs)
    
    def get(self, **kwargs) -> Optional[T]:
        """
        Obtiene un registro único según los criterios
        
        Args:
            **kwargs: Criterios de búsqueda
            
        Returns:
            Instancia del modelo o None si no existe
            
        Example:
            repo.get(id=1)
        """
        try:
            return self.model.objects.get(**kwargs)
        except ObjectDoesNotExist:
            return None
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Obtiene un registro por su ID
        
        Args:
            id: ID del registro
            
        Returns:
            Instancia del modelo o None si no existe
        """
        return self.get(id=id)
    
    def create(self, **kwargs) -> T:
        """
        Crea un nuevo registro
        
        Args:
            **kwargs: Datos para crear el registro
            
        Returns:
            Instancia del modelo creado
            
        Example:
            repo.create(nombre='Empresa ABC', ruc='12345678901')
        """
        return self.model.objects.create(**kwargs)
    
    def bulk_create(self, objects: List[T], batch_size: Optional[int] = None) -> List[T]:
        """
        Crea múltiples registros de forma eficiente
        
        Args:
            objects: Lista de instancias del modelo a crear
            batch_size: Tamaño del lote para inserción
            
        Returns:
            Lista de instancias creadas
        """
        return self.model.objects.bulk_create(objects, batch_size=batch_size)
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Actualiza un registro por su ID
        
        Args:
            id: ID del registro a actualizar
            **kwargs: Campos a actualizar
            
        Returns:
            Instancia actualizada o None si no existe
            
        Example:
            repo.update(id=1, nombre='Nuevo Nombre')
        """
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return None
    
    def update_or_create(self, defaults: Dict[str, Any], **kwargs) -> tuple[T, bool]:
        """
        Actualiza un registro existente o crea uno nuevo
        
        Args:
            defaults: Valores a actualizar/crear
            **kwargs: Criterios de búsqueda
            
        Returns:
            Tupla (instancia, created) donde created es True si fue creado
            
        Example:
            repo.update_or_create(
                defaults={'nombre': 'Empresa ABC'},
                ruc='12345678901'
            )
        """
        return self.model.objects.update_or_create(defaults=defaults, **kwargs)
    
    def delete(self, id: int) -> bool:
        """
        Elimina un registro por su ID
        
        Args:
            id: ID del registro a eliminar
            
        Returns:
            True si fue eliminado, False si no existía
        """
        instance = self.get_by_id(id)
        if instance:
            instance.delete()
            return True
        return False
    
    def exists(self, **kwargs) -> bool:
        """
        Verifica si existe un registro con los criterios dados
        
        Args:
            **kwargs: Criterios de búsqueda
            
        Returns:
            True si existe al menos un registro, False en caso contrario
            
        Example:
            repo.exists(ruc='12345678901')
        """
        return self.model.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        """
        Cuenta los registros que cumplen los criterios
        
        Args:
            **kwargs: Criterios de filtrado (opcional)
            
        Returns:
            Número de registros
            
        Example:
            repo.count(tipo='ingreso')
        """
        if kwargs:
            return self.model.objects.filter(**kwargs).count()
        return self.model.objects.count()
    
    def first(self, **kwargs) -> Optional[T]:
        """
        Obtiene el primer registro según los criterios
        
        Args:
            **kwargs: Criterios de filtrado (opcional)
            
        Returns:
            Primera instancia encontrada o None
        """
        queryset = self.filter(**kwargs) if kwargs else self.all()
        return queryset.first()
    
    def last(self, **kwargs) -> Optional[T]:
        """
        Obtiene el último registro según los criterios
        
        Args:
            **kwargs: Criterios de filtrado (opcional)
            
        Returns:
            Última instancia encontrada o None
        """
        queryset = self.filter(**kwargs) if kwargs else self.all()
        return queryset.last()
    
    def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **kwargs) -> tuple[T, bool]:
        """
        Obtiene un registro existente o crea uno nuevo
        
        Args:
            defaults: Valores adicionales para creación
            **kwargs: Criterios de búsqueda
            
        Returns:
            Tupla (instancia, created) donde created es True si fue creado
            
        Example:
            repo.get_or_create(
                ruc='12345678901',
                defaults={'nombre': 'Empresa ABC'}
            )
        """
        return self.model.objects.get_or_create(defaults=defaults, **kwargs)
    
    def exclude(self, **kwargs) -> QuerySet[T]:
        """
        Excluye registros que cumplan los criterios
        
        Args:
            **kwargs: Criterios de exclusión
            
        Returns:
            QuerySet excluyendo los registros
            
        Example:
            repo.exclude(tipo='egreso')
        """
        return self.model.objects.exclude(**kwargs)
    
    def order_by(self, *fields) -> QuerySet[T]:
        """
        Ordena los registros por los campos especificados
        
        Args:
            *fields: Campos por los que ordenar (usar '-' para descendente)
            
        Returns:
            QuerySet ordenado
            
        Example:
            repo.order_by('-fecha', 'monto')
        """
        return self.model.objects.order_by(*fields)
    
    def values(self, *fields, **kwargs) -> QuerySet:
        """
        Obtiene valores específicos como diccionarios
        
        Args:
            *fields: Campos a incluir
            **kwargs: Criterios de filtrado
            
        Returns:
            QuerySet de diccionarios
            
        Example:
            repo.values('id', 'nombre', tipo='ingreso')
        """
        queryset = self.filter(**kwargs) if kwargs else self.all()
        return queryset.values(*fields)
    
    def values_list(self, *fields, flat: bool = False, **kwargs) -> QuerySet:
        """
        Obtiene valores específicos como tuplas o lista plana
        
        Args:
            *fields: Campos a incluir
            flat: Si True y solo se pide un campo, devuelve lista plana
            **kwargs: Criterios de filtrado
            
        Returns:
            QuerySet de tuplas o valores planos
            
        Example:
            repo.values_list('id', flat=True)
        """
        queryset = self.filter(**kwargs) if kwargs else self.all()
        return queryset.values_list(*fields, flat=flat)
    
    def distinct(self, *fields) -> QuerySet[T]:
        """
        Obtiene registros únicos
        
        Args:
            *fields: Campos para determinar unicidad (opcional)
            
        Returns:
            QuerySet con registros distintos
        """
        return self.model.objects.distinct(*fields)
    
    def select_related(self, *fields) -> QuerySet[T]:
        """
        Optimiza queries con relaciones ForeignKey y OneToOne
        
        Args:
            *fields: Campos relacionados a incluir
            
        Returns:
            QuerySet optimizado
            
        Example:
            repo.select_related('empresa', 'categoria')
        """
        return self.model.objects.select_related(*fields)
    
    def prefetch_related(self, *fields) -> QuerySet[T]:
        """
        Optimiza queries con relaciones ManyToMany y reverse ForeignKey
        
        Args:
            *fields: Campos relacionados a pre-cargar
            
        Returns:
            QuerySet optimizado
        """
        return self.model.objects.prefetch_related(*fields)
    
    def aggregate(self, **kwargs):
        """
        Realiza agregaciones sobre el QuerySet
        
        Args:
            **kwargs: Funciones de agregación
            
        Returns:
            Diccionario con resultados de agregación
            
        Example:
            from django.db.models import Sum, Avg
            repo.aggregate(total=Sum('monto'), promedio=Avg('monto'))
        """
        return self.model.objects.aggregate(**kwargs)
    
    def annotate(self, **kwargs) -> QuerySet[T]:
        """
        Añade anotaciones calculadas a cada registro
        
        Args:
            **kwargs: Anotaciones a añadir
            
        Returns:
            QuerySet anotado
            
        Example:
            from django.db.models import Count
            repo.annotate(num_transacciones=Count('transaccion'))
        """
        return self.model.objects.annotate(**kwargs)