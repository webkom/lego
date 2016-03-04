# -*- coding: utf--8 -*-
from django.db import models

from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import User


class Content(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    ingress = models.TextField()
    text = models.TextField(blank=True)

    def __str__(self):
        return self.title + '(by: {})'.format(self.author)
