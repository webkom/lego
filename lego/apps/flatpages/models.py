from django.db import models

from lego.apps.content.models import SlugModel
from lego.apps.files.models import FileField
from lego.apps.flatpages.permissions import PagePermissionHandler
from lego.utils.models import BasisModel


class Page(BasisModel, SlugModel):
    title = models.CharField('title', max_length=200)
    content = models.TextField('content')
    picture = FileField()
    slug_field = 'title'

    class Meta:
        permission_handler = PagePermissionHandler()

    def __str__(self):
        return "%s -- %s" % (self.slug, self.title)
