from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lego.apps.content.models import SlugModel
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class Page(MPTTModel, BasisModel, ObjectPermissionsModel, SlugModel):
    title = models.CharField('title', max_length=200)
    content = models.TextField('content')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __str__(self):
        return "%s -- %s" % (self.slug, self.title)
