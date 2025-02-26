from django.db import models

from lego.apps.files.models import FileField
from lego.apps.lending.permissions import LendableObjectPermissionHandler
from lego.apps.permissions.constants import VIEW
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class LendableObject(BasisModel, ObjectPermissionsModel):
    title = models.CharField(max_length=128, null=False, blank=False)
    contact_email = models.EmailField()
    description = models.TextField(null=False, blank=True)
    image = FileField(related_name="lendable_object_image")
    location = models.CharField(max_length=128, null=False, blank=True)

    class Meta:
        permission_handler = LendableObjectPermissionHandler()

    def can_lend(self, user: User) -> bool:
        """
        Check if the user can lend the object.
        They can lend if they have view permission from object permissions.
        This is necessary because admins can see all objects, but should not be able to lend them
        unless given explicit permission.
        """
        return self._meta.permission_handler.has_object_permissions(user, VIEW, self)
