from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lego.apps.content.models import SlugModel
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class Page(MPTTModel, BasisModel, ObjectPermissionsModel, SlugModel):
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class Meta:
        verbose_name = _('flatpage')
        verbose_name_plural = _('flatpages')

    def __str__(self):
        return "%s -- %s" % (self.slug, self.title)
