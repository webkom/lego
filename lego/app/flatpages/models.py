# -*- coding: utf8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from basis.models import BasisModel
from markdown import markdown

from .managers import PublicPageManager, InternalPageManager


class Page(BasisModel):
    title = models.CharField(_('title'), max_length=200)
    slug = models.CharField(_('slug'), unique=True, db_index=True, max_length=100)

    content = models.TextField(_('content'))

    toc = models.BooleanField(default=False, verbose_name=_('Needs table of contents'))
    require_auth = models.BooleanField(default=False,
                                       verbose_name=_('Can only be viewed by authenticated users'))
    require_abakom = models.BooleanField(default=False,
                                         verbose_name=_('Can only be viewed by abakom users'))

    public_objects = PublicPageManager()
    internal_objects = InternalPageManager()

    class Meta:
        verbose_name = _('flatpage')
        verbose_name_plural = _('flatpages')
        ordering = ('slug',)

    def __str__(self):
        return "%s -- %s" % (self.slug, self.title)

    def save(self, *args, **kwargs):
        if self.require_abakom and not self.require_auth:
            self.require_auth = True
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.slug

    def rendered_content(self):
        return markdown(self.content)
