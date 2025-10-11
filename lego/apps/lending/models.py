from django.db import models

from lego.apps.files.models import FileField
from lego.apps.lending.constants import (
    LENDING_CATEGORIES,
    LENDING_CHOICE_STATUSES,
    LENDING_REQUEST_STATUSES,
    OTHER,
)
from lego.apps.lending.permissions import (
    LendableObjectPermissionHandler,
    LendingRequestPermissionHandler,
)
from lego.apps.permissions.constants import VIEW
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class LendableObject(BasisModel, ObjectPermissionsModel):
    title = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = FileField(related_name="lendable_object_image")
    location = models.CharField(max_length=128, null=False, blank=True)
    category = models.CharField(
        max_length=64,
        choices=LENDING_CATEGORIES,
        default=OTHER,
        null=False,
        blank=False,
    )

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


class LendingRequest(BasisModel):
    lendable_object = models.ForeignKey(LendableObject, on_delete=models.CASCADE)
    status = models.CharField(
        choices=LENDING_CHOICE_STATUSES,
        null=False,
        blank=True,
        default=LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"],
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        permission_handler = LendingRequestPermissionHandler()
        indexes = [
            models.Index(fields=["created_by"]),
            models.Index(fields=["lendable_object"]),
        ]


class TimelineEntry(BasisModel):
    lending_request = models.ForeignKey(
        LendingRequest, on_delete=models.CASCADE, related_name="timeline_entries"
    )
    message = models.TextField(blank=False, null=False)
    is_system = models.BooleanField(default=False, blank=True, null=False)
    status = models.CharField(
        choices=LENDING_CHOICE_STATUSES,
        null=True,
        blank=True,
    )
