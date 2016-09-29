from django.db import models

from lego.apps.content.models import SlugContent
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class Article(SlugContent, BasisModel, ObjectPermissionsModel):

    author = models.ForeignKey('users.User')

    class Meta:
        abstract = False
