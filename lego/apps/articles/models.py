from basis.models import BasisModel

from lego.apps.content.models import Content
from lego.apps.permissions.models import ObjectPermissionsModel


class Article(Content, BasisModel, ObjectPermissionsModel):
    class Meta:
        # This is needed since all the models we inherit from
        # are abstract:
        abstract = False
