from datetime import datetime, timedelta, timezone, tzinfo

from django.db import models
from lego.apps.files.fields import ImageField
from lego.apps.files.models import FileField
from lego.apps.lending.permissions import LendingInstancePermissionHandler
from lego.apps.lending.validators import responsible_roles_validator
from django.contrib.postgres.fields import ArrayField
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users import constants
from lego.apps.lending.managers import LendingInstanceManager
from lego.apps.users.models import User


from lego.utils.models import BasisModel


# Create your models here.


class LendableObject(BasisModel, ObjectPermissionsModel):
    title = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    has_contract = models.BooleanField(default=False, null=False, blank=False)
    max_lending_period = models.DurationField(
        null=True, blank=False, default=timedelta(days=7)
    )
    responsible_groups = models.ManyToManyField("users.AbakusGroup")
    responsible_roles = ArrayField(
        models.CharField(
            max_length=30,
            choices=constants.ROLES,
        ),
        default=list([constants.MEMBER]),
        validators=[responsible_roles_validator],
    )  
    image = FileField(related_name="lendable_object_images")
    location = models.CharField(max_length=128, null=False, blank=True)

    @property
    def get_furthest_booking_date(self):
        return timezone.now() + timedelta(days=14)

    class Meta:
        abstract = False


class LendingInstance(BasisModel, ObjectPermissionsModel):
    lendable_object = models.ForeignKey(LendableObject, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    pending = models.BooleanField(default=True)
    comment = models.TextField(null=False, blank=True)

    objects = LendingInstanceManager()  # type: ignore

    @property
    def active(self):
        return timezone.now() < self.end_date and timezone.now() > self.start_date

    class Meta:
        abstract = False
        permission_handler = LendingInstancePermissionHandler()
