from basis.models import BasisModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lego.permissions.models import ObjectPermissionsModel


class Comment(BasisModel, ObjectPermissionsModel):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    parent = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.created_by, self.text[:30])
