# -*- coding: utf--8 -*-
from basis.models import BasisModel
from django.db import models
from django.utils.translation import ugettext_lazy as _


from lego.users.models import User, AbakusGroup


class Article(BasisModel):
    title = models.CharField(_('title'), max_length=255)
    author = models.ForeignKey(User, editable=False, null=True, verbose_name='author')

    ingress = models.TextField(_('ingress'))
    text = models.TextField(_('article text'), blank=True)

    users_can_edit = models.ManyToManyField(User, related_name='editable_articles')
    groups_can_edit = models.ManyToManyField(AbakusGroup, related_name='editable_articles')
    can_view = models.ManyToManyField(AbakusGroup, related_name='viewable_articles')

    def __str__(self):
        return self.title
