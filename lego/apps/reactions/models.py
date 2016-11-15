from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class ReactionManager(BasisModelManager):
    def get_queryset(self):
        return super(ReactionManager, self).get_queryset().select_related('created_by')


class ReactionType(BasisModel):
    short_code = models.CharField(max_length=40, primary_key=True)
    unicode = models.CharField(max_length=24, db_index=True)


class Reaction(BasisModel):
    type = models.ForeignKey(ReactionType)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()

    objects = ReactionManager()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '{0} - {1}'.format(self.created_by, self.type_id)
