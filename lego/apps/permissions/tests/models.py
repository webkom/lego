from django.db import models
from django.utils.translation import ugettext_lazy as _

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class TestModel(BasisModel, ObjectPermissionsModel):
    name = models.CharField(_('name'), max_length=30)
