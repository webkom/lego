from datetime import datetime, timedelta, timezone, tzinfo

from django.db import models

from lego.apps.users import constants
from lego.apps.lending.managers import LendingInstanceManager


from lego.utils.models import BasisModel


# Create your models here.


class LendableObject(BasisModel):
    title = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    has_contract = models.BooleanField(default=False, null=False, blank=False)
    max_lending_period = models.DurationField(null=True, blank=False)
    responsible_groups = models.ManyToManyField("users.AbakusGroup")
    responsible_role = models.CharField(
        max_length=30, choices=constants.ROLES, default=constants.MEMBER
    )
    location = models.CharField(max_length=128, null=False, blank=False)

    @property
    def get_furthest_booking_date(self):
        return timezone.now() + timedelta(days=14)


class LendingInstance(BasisModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    lendable_object = models.ForeignKey(LendableObject, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    pending = models.BooleanField(default=True)

    objects = LendingInstanceManager()  # type: ignore

    @property
    def active(self):
        return timezone.now() < self.end_date and timezone.now() > self.start_date
