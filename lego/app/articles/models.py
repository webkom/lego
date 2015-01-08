# -*- coding: utf--8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


from lego.users.models import User
from lego.permissions.models import ObjectPermissionsModel


class Article(ObjectPermissionsModel):
    title = models.CharField(_('title'), max_length=255)
    author = models.ForeignKey(User, _('author'), editable=False, null=True)

    ingress = models.TextField(_('ingress'))
    text = models.TextField(_('article text'), blank=True)

    def __str__(self):
        return self.title
