from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.utils import timezone

from .managers import BasisModelManager, PersistentModelManager


class TimeStampModel(models.Model):
    """
    Attach created_at and updated_at fields automatically on all model instances.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class PersistentModel(models.Model):
    """
    Hide 'deleted' models from default queryset. Replaces the manager to accomplish this.
    Remember to inherit from PersistentModelManager when you replaces a manager on a child-class.
    """
    deleted = models.BooleanField(default=False, editable=False)

    objects = PersistentModelManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        default_manager_name = 'objects'

    def delete(self, using=None, force=False):
        if force:
            super(PersistentModel, self).delete(using)
        else:
            pre_delete.send(sender=self.__class__, instance=self)
            self.deleted = True
            self.save()
            post_delete.send(sender=self.__class__, instance=self)

    def restore(self, *args, **kwargs):
        self.deleted = False
        self.save(*args, **kwargs)


class BasisModel(PersistentModel, TimeStampModel):
    """
    Based on the PersistentModel and the TimeStampModel. Attach created_by and updated_by fields
    on all instances. A BasisModelSerializer is required when using this with rest-framework.
    """
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, default=None,
                                   editable=False, related_name="%(class)s_created", db_index=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, default=None,
                                   editable=False, related_name="%(class)s_updated")

    objects = BasisModelManager()

    class Meta:
        abstract = True
        default_manager_name = 'objects'

    def save(self, *args, **kwargs):
        try:
            current_user = kwargs.pop('current_user', None) or self.current_user
            if not self.id:
                self.created_by = current_user
            self.updated_by = current_user
        except AttributeError:
            pass
        return super().save(*args, **kwargs)
