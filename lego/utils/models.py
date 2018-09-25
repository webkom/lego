from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.utils import timezone

from lego.utils.decorators import abakus_cached_property

from .managers import BasisModelManager, PersistentModelManager


class CachedModel(models.Model):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_properties = {}
        for model_class in self.__class__.__mro__:
            class_items = model_class.__dict__.items()
            for k, v in class_items:
                if isinstance(v, abakus_cached_property):
                    self._cached_properties[k] = v

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for cached_property, decorator in self._cached_properties.items():
            if cached_property in self.__dict__:
                if decorator.delete_on_save:
                    del self.__dict__[cached_property]


class TimeStampModel(CachedModel):
    """
    Attach created_at and updated_at fields automatically on all model instances.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class PersistentModel(CachedModel):
    """
    Hide 'deleted' models from default queryset. Replaces the manager to accomplish this.
    Remember to inherit from PersistentModelManager when you replaces a manager on a child-class.
    """
    deleted = models.BooleanField(default=False, editable=False, db_index=True)

    objects = PersistentModelManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        default_manager_name = 'objects'

    def delete(self, using=None, force=False):
        if force:
            super().delete(using)
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
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, default=None, editable=False,
        related_name="%(class)s_created", db_index=True, on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, default=None, editable=False,
        related_name="%(class)s_updated", on_delete=models.SET_NULL
    )

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
