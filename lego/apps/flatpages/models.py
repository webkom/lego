from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lego.apps.content.models import SlugModel
from lego.utils.managers import TreeBasisManager
from lego.apps.files.models import FileField
from lego.utils.models import BasisModel


class Page(MPTTModel, BasisModel, SlugModel):
    title = models.CharField('title', max_length=200)
    content = models.TextField('content')
    picture = FileField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    slug_field = 'title'

    objects = TreeBasisManager()

    def __str__(self):
        return "%s -- %s" % (self.slug, self.title)
