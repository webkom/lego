from basis.models import BasisModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lego.users.models import User


class Comment(BasisModel):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    # author = models.ForeignKey(User)

    @property
    def source(self):
        return '{0}-{1}'.format(self.content_type.app_label, self.object_id)

    def __str__(self):
        return '{0} - {1}'.format(self.author, self.text[:30])
