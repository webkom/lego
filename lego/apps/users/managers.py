from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import Q, QuerySet

if TYPE_CHECKING:
    from lego.apps.users.models import Penalty, PenaltyGroup

from django.conf import settings
from django.utils import timezone

from mptt.managers import TreeManager

from lego.utils.managers import PersistentModelManager


class AbakusGroupManager(TreeManager, PersistentModelManager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class AbakusGroupManagerWithoutText(AbakusGroupManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().defer("text")


class AbakusUserManager(UserManager, PersistentModelManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        We do not set is_staff or is_superuser as they are a @cached_property
        in our User model.
        """
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """
        We do not set is_staff or is_superuser as they are a @cached_property
        in our User model.
        """
        return self._create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(
            Q(username__iexact=username.lower()) | Q(email__iexact=username.lower())
        )


class MembershipManager(PersistentModelManager):
    def get_by_natural_key(self, username, abakus_group_name):
        return self.get(
            user__username__iexact=username.lower(),
            abakus_group__name__iexact=abakus_group_name.lower(),
        )


class UserPenaltyManager(PersistentModelManager["Penalty"]):
    def valid(self) -> QuerySet["Penalty"]:
        from lego.apps.users.models import Penalty

        offset = Penalty.penalty_offset(timezone.now(), False)
        return super().filter(activation_time__gt=timezone.now() - offset)


class UserPenaltyGroupManager(PersistentModelManager["PenaltyGroup"]):
    def create(self, *args, **kwargs) -> PenaltyGroup:
        from lego.apps.users.models import Penalty
        from lego.apps.users.notifications import PenaltyNotification

        penalty_group = super().create(*args, **kwargs)

        last_active_penalty = (
            Penalty.objects.filter(
                penalty_group__user=penalty_group.user,
            )
            .order_by("-activation_time")
            .first()
        )

        new_activation_time = (
            last_active_penalty.exact_expiration
            if last_active_penalty
            else penalty_group.created_at
        )

        penalties = []

        for _ in range(kwargs["weight"]):
            penalty = Penalty(penalty_group=penalty_group)
            penalty.activation_time = new_activation_time

            new_activation_time = penalty.exact_expiration

            penalties.append(penalty)

        Penalty.objects.bulk_create(penalties)

        # Send Notification
        notification = PenaltyNotification(penalty_group.user, penalty=penalty_group)
        notification.notify()

        return penalty_group

    def valid(self) -> QuerySet["PenaltyGroup"]:
        from django.db.models import F

        from lego.apps.users.models import PenaltyGroup

        filtered_result = PenaltyGroup.objects.filter(
            id__in=[
                pg.id
                for pg in super().annotate(penalty_count=models.Count(F("penalties")))
                if pg.activation_time
                > timezone.now() - timedelta(days=settings.PENALTY_DURATION.days)
            ]
        )

        return filtered_result
