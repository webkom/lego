from django.db import models

from lego.apps.content.models import Content
from lego.apps.files.models import FileField
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class Article(Content, BasisModel, ObjectPermissionsModel):

    author = models.ForeignKey('users.User')
    cover = FileField(related_name='article_covers')

    class Meta:
        abstract = False
