from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lego.utils.models import BasisModel


class Follower(BasisModel):
    follower = models.ForeignKey('users.User', related_name='following')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    following = GenericForeignKey()
