from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base model that adds created_at and updated_at fields.
    Every model in an e-commerce system should track when it was created/modified.
    """
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract model that adds soft‑delete capability.
    Prevents accidental permanent data loss and enables "undo" features.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Combined base model – use this for most e-commerce entities.
    """
    class Meta:
        abstract = True