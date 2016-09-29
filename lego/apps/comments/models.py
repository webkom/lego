from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class CommentManager(BasisModelManager):
    def get_queryset(self):
        return super(CommentManager, self).get_queryset().select_related('created_by')


class Comment(BasisModel, ObjectPermissionsModel):

    text = models.TextField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    parent = models.ForeignKey('self', null=True, blank=True)

    objects = CommentManager()

    def __str__(self):
        return '{0} - {1}'.format(self.created_by, self.text[:30])
