from basis.models import BasisModel

from lego.apps.content.models import SlugContent
from lego.apps.permissions.models import ObjectPermissionsModel


class Article(SlugContent, BasisModel, ObjectPermissionsModel):
    class Meta:
        # This is needed since all the models we inherit from
        # are abstract:
        abstract = False
