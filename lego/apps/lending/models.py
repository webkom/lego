from django.db import models

from lego.apps.files.models import FileField
from lego.apps.lending.permissions import LendableObjectPermissionHandler
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class LendableObject(BasisModel, ObjectPermissionsModel):
    title = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = FileField(related_name="lendable_object_image")
    location = models.CharField(max_length=128, null=False, blank=True)

    class Meta:
        permission_handler = LendableObjectPermissionHandler()
