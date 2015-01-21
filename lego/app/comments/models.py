# -*- coding: utf8 -*-
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from basis.models import PersistentModel

from lego.users.models import User


class Comment(PersistentModel):
    content = models.TextField()

    author = models.ForeignKey(User, related_name='comments')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return '{0} - {1}'.format(self.author, self.content[:30])
