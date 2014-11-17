# -*- coding: utf8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from markdown import markdown

from lego.permissions.models import ObjectPermissionsModel


class Page(ObjectPermissionsModel):
    title = models.CharField(_('title'), max_length=200)
    slug = models.CharField(_('slug'), unique=True, db_index=True, max_length=100)

    content = models.TextField(_('content'))

    toc = models.BooleanField(default=False, verbose_name=_('Needs table of contents'))

    class Meta:
        verbose_name = _('flatpage')
        verbose_name_plural = _('flatpages')
        ordering = ('slug',)

    def __str__(self):
        return "%s -- %s" % (self.slug, self.title)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.slug

    def rendered_content(self):
        return markdown(self.content)
