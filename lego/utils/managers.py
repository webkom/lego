from django.db import models, transaction
from django.db.models.signals import post_delete, pre_delete


class PersistentModelQuerySet(models.QuerySet):
    """
    This queryset makes sure we keep persistent models when we do .delete() on a queryset.
    """

    def delete(self, force=False):
        """
        Add support for the queryset.delete method. Use select_for_update and set deleted to True.
        Manually send post_delete signals on delete.
        """
        if force:
            return super().delete()
        else:
            with transaction.atomic(savepoint=False):
                instances = super().select_for_update()
                for instance in instances:
                    pre_delete.send(sender=instance.__class__, instance=instance)
                delete_result = instances.delete()
                for instance in instances:
                    post_delete.send(sender=instance.__class__, instance=instance)
                return delete_result


class PersistentModelManager(models.Manager):
    def get_queryset(self):
        return PersistentModelQuerySet(self.model, using=self._db).filter(deleted=False)


class BasisModelManager(PersistentModelManager):
    def create(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        kwargs['created_by'] = user
        kwargs['updated_by'] = user
        instance = super().create(*args, **kwargs)
        return instance
