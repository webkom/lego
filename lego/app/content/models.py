# -*- coding: utf--8 -*-
from django.db import models
from django.utils.text import slugify

from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import User


class Content(ObjectPermissionsModel):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    ingress = models.TextField()
    text = models.TextField(blank=True)
    slug = models.SlugField(null=True, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify('{}-{}'.format(self.id, self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title + '(by: {})'.format(self.author)
