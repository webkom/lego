from basis.models import BasisModel
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lego.permissions.models import ObjectPermissionsModel


class TestModel(BasisModel, ObjectPermissionsModel):
    name = models.CharField(_('name'), max_length=30)
