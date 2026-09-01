from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet personalizado para soft delete"""

    def delete(self):
        """Soft delete para múltiples registros"""
        return self.update(
            is_active=False,
            deleted_at=timezone.now(),
        )

    def hard_delete(self):
        """Borrado físico real"""
        return super().delete()

    def active(self):
        """Solo registros activos"""
        return self.filter(is_active=True)

    def inactive(self):
        """Solo registros inactivos (eliminados vía soft delete)"""
        return self.filter(is_active=False)


class SoftDeleteManager(models.Manager):
    """Manager que filtra registros inactivos por defecto"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_active=True)

    def all_with_deleted(self):
        """Acceso a todos los registros incluyendo eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Solo registros eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_active=False)


class BaseModel(models.Model):
    """
    Modelo base abstracto para todos los modelos del proyecto.
    Incluye campos de auditoría y soft delete.

    IMPORTANTE:
    - `is_active` es la ÚNICA fuente de verdad para determinar si un
      registro está eliminado o no. Todo el comportamiento (manager,
      constraints, queries) debe basarse exclusivamente en este campo.
    - `deleted_at` es puramente informativo: guarda la fecha de la
      última desactivación, pero NUNCA debe usarse para filtrar,
      determinar comportamiento, ni en unique constraints. Si en algún
      modelo hijo necesitas condicionar algo por "eliminado o no",
      condiciona por `is_active`, no por `deleted_at`.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Solo informativo: fecha de la última desactivación. No se usa para lógica de negocio.",
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

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

        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Borrado físico permanente"""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restaurar un registro eliminado"""
        self.is_active = True
        self.save()

    @property
    def is_deleted(self):
        """Verifica si el registro está eliminado"""
        return not self.is_active

    def __str__(self):
        return f"{self.__class__.__name__} - {self.pk}"