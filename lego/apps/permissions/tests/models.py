from django.db import models

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class TestModel(BasisModel, ObjectPermissionsModel):  # type: ignore
    name = models.CharField("name", max_length=30)
