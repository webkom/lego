from django.db import models

from lego.apps.content.fields import ContentField
from lego.apps.content.models import SlugModel
from lego.apps.files.models import FileField
from lego.apps.flatpages.permissions import PagePermissionHandler
from lego.utils.models import BasisModel
from lego.apps.flatpages import constants


class Page(BasisModel, SlugModel):
    title = models.CharField("title", max_length=200)
    content = ContentField(allow_images=True)
    picture = FileField()
    slug_field = "title"
    category = models.CharField(
        max_length=50, choices=constants.CATEGORIES, default=constants.GENERAL)

    class Meta:
        permission_handler = PagePermissionHandler()

    def __str__(self):
        return "%s -- %s" % (self.slug, self.title)
