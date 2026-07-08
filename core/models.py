from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet personalizado para soft delete"""
    
    def delete(self):
        """Soft delete para múltiples registros"""
        return self.update(
            deleted_at=timezone.now(),
            is_active=False
        )
    
    def hard_delete(self):
        """Borrado físico real"""
        return super().delete()
    
    def active(self):
        """Solo registros activos"""
        return self.filter(is_active=True, deleted_at__isnull=True)
    
    def inactive(self):
        """Solo registros inactivos"""
        return self.filter(is_active=False)
    
    def deleted(self):
        """Solo registros eliminados (soft delete)"""
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    """Manager que filtra registros eliminados por defecto"""
    
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True,
            is_active=True
        )
    
    def all_with_deleted(self):
        """Acceso a todos los registros incluyendo eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """Solo registros eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=False
        )


class BaseModel(models.Model):
    """
    Modelo base abstracto para todos los modelos del proyecto.
    Incluye campos de auditoría y soft delete.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Soft delete por defecto.
        
        Args:
            using: Base de datos a usar
            keep_parents: Mantener registros padre
            hard: Si es True, ejecuta borrado físico
        """
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """Borrado físico permanente"""
        return super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restaurar un registro eliminado"""
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    def deactivate(self):
        """Desactivar sin marcar como eliminado"""
        self.is_active = False
        self.save()
    
    def activate(self):
        """Activar registro"""
        self.is_active = True
        self.save()
    
    @property
    def is_deleted(self):
        """Verifica si el registro está eliminado"""
        return self.deleted_at is not None
    
    def __str__(self):
        return f"{self.__class__.__name__} - {self.pk}"