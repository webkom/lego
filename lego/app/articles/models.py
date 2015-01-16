# -*- coding: utf--8 -*-
from django.db import models

from lego.users.models import User
from lego.permissions.models import ObjectPermissionsModel


class Article(ObjectPermissionsModel):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, editable=False, null=True)

    ingress = models.TextField()
    text = models.TextField(blank=True)

    def __str__(self):
        return self.title
