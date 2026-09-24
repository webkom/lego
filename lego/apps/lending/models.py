from datetime import datetime

from django.db import models, transaction
from django.utils import timezone

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
    lendable_objects = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="lendable_bundle_objects"
    )

    class Meta:
        permission_handler = LendableObjectPermissionHandler()

    def delete(self, using=None, force=False) -> tuple[int, dict[str, int]]:
        if force:
            return super().delete(using=using, force=force)

        with transaction.atomic():
            for lending_request in self.lendingrequest_set.all():
                lending_request.delete(force=False)
            return super().delete(using=using, force=force)

    def can_lend(self, user: User) -> bool:
        """
        Check if the user can lend the object.
        They can lend if they have view permission from object permissions.
        This is necessary because admins can see all objects, but should not be able to lend them
        unless given explicit permission.
        """
        return self._meta.permission_handler.has_object_permissions(user, VIEW, self)

    def contains(self, other: "LendableObject") -> bool:
        """True if `other` is this object, or reachable through nested `lendable_objects`."""
        if self == other:
            return True
        return any(child.contains(other) for child in self.lendable_objects.all())

    def containing_bundle_ids(self) -> set[int]:
        """Ids of every bundle that (transitively) contains this object."""
        ids: set[int] = set()
        for parent in self.lendable_bundle_objects.all():
            if parent.id not in ids:
                ids.add(parent.id)
                ids |= parent.containing_bundle_ids()
        return ids

    def _approved_overlapping_requests(
        self, start_date, end_date, exclude_request_id: int | None = None
    ):
        """
        Approved requests overlapping [start_date, end_date), directly on this object
        or on any bundle (at any nesting depth) that contains it.
        """
        approved_status = LENDING_REQUEST_STATUSES["LENDING_APPROVED"]["value"]
        relevant_object_ids = {self.id, *self.containing_bundle_ids()}
        requests = LendingRequest.objects.filter(
            lendable_object_id__in=relevant_object_ids,
            status=approved_status,
            start_date__lt=end_date,
            end_date__gt=start_date,
        ).select_related("created_by")
        if exclude_request_id is not None:
            requests = requests.exclude(id=exclude_request_id)
        return requests

    def availability(
        self, month: int, year: int
    ) -> list[tuple[str, str, str | None, str | None]]:
        children = list(self.lendable_objects.all())
        if children:
            child_ranges = [set(child.availability(month, year)) for child in children]
            return list(set().union(*child_ranges))

        start_of_month = timezone.make_aware(datetime(year, month, 1))
        next_month = month % 12 + 1
        next_month_year = year + (month == 12)
        start_of_next_month = timezone.make_aware(
            datetime(next_month_year, next_month, 1)
        )

        overlapping_requests = self._approved_overlapping_requests(
            start_of_month, start_of_next_month
        ).order_by("start_date")

        ranges = []
        for lending_request in overlapping_requests:
            range_start = max(lending_request.start_date, start_of_month)
            range_end = min(lending_request.end_date, start_of_next_month)
            created_by = lending_request.created_by
            fullname = created_by.get_full_name() if created_by else None
            username = created_by.username if created_by else None
            ranges.append(
                (range_start.isoformat(), range_end.isoformat(), fullname, username)
            )
        return ranges

    def is_available(
        self, start_date, end_date, exclude_request_id: int | None = None
    ) -> bool:
        """
        True if there is no approved lending request overlapping [start_date, end_date).
        A bundle is available only when every one of its children is.
        """
        children = list(self.lendable_objects.all())
        if children:
            return all(
                child.is_available(
                    start_date, end_date, exclude_request_id=exclude_request_id
                )
                for child in children
            )

        return not self._approved_overlapping_requests(
            start_date, end_date, exclude_request_id=exclude_request_id
        ).exists()

    @staticmethod
    def unavailable_ids(start_date, end_date) -> set[int]:
        """
        Ids of every LendableObject with an approved request overlapping
        [start_date, end_date), directly or via a bundle containing it.
        """
        approved_status = LENDING_REQUEST_STATUSES["LENDING_APPROVED"]["value"]
        overlapping = LendingRequest.objects.filter(
            status=approved_status, start_date__lt=end_date, end_date__gt=start_date
        )
        directly_booked = overlapping.values_list("lendable_object_id", flat=True)
        booked_via_bundle = overlapping.filter(
            lendable_object__lendable_objects__isnull=False
        ).values_list("lendable_object__lendable_objects", flat=True)
        return set(directly_booked) | set(booked_via_bundle)


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
    archived = models.BooleanField(default=False, blank=True, null=False)

    class Meta:
        permission_handler = LendingRequestPermissionHandler()
        indexes = [
            models.Index(fields=["created_by"]),
            models.Index(fields=["lendable_object"]),
        ]

    def delete(self, using=None, force=False) -> tuple[int, dict[str, int]]:
        if force:
            return super().delete(using=using, force=force)

        with transaction.atomic():
            for timeline_entry in self.timeline_entries.all():
                timeline_entry.delete(force=False)
            return super().delete(using=using, force=force)


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
