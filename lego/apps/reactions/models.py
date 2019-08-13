from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from rest_framework.exceptions import ValidationError

from lego.apps.reactions.permissions import ReactionPermissionHandler
from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class ReactionManager(BasisModelManager):
    def get_queryset(self):
        return super().get_queryset().select_related("created_by")


class ReactionType(BasisModel):
    short_code = models.CharField(max_length=40, primary_key=True)
    unicode = models.CharField(max_length=24, db_index=True)


class Reaction(BasisModel):
    type = models.ForeignKey(ReactionType, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()

    objects = ReactionManager()

    class Meta:
        permission_handler = ReactionPermissionHandler()
        constraints = [
            models.UniqueConstraint(fields=['journal_id', 'volume_number'],
                                    name='name of constraint')
        ]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.created_by} - {self.type_id}"

    def delete(self, using=None, force=False):
        super().delete(using, force=True)
