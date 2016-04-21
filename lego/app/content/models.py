# -*- coding: utf--8 -*-
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from lego.app.comments.models import Comment
from lego.users.models import User


class Content(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    description = models.TextField()
    text = models.TextField(blank=True)
    comments = GenericRelation(Comment)

    def __str__(self):
        return self.title + '(by: {})'.format(self.author)

    @property
    def comment_target(self):
        return '{0}-{1}'.format(self._meta.app_label, self.pk)
