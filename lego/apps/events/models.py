from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import CharField, Count, ManyToManyField, QuerySet, Sum
from django.utils import timezone

from lego.apps.action_handlers.events import handle_event
from lego.apps.companies.models import Company
from lego.apps.content.models import Content
from lego.apps.events import constants
from lego.apps.events.exceptions import (
    EventHasClosed,
    EventNotReady,
    NoSuchPool,
    NoSuchRegistration,
    NotRegisteredPhotoConsents,
    RegistrationExists,
    RegistrationsExistInPool,
    UnansweredSurveyException,
)
from lego.apps.events.permissions import (
    EventPermissionHandler,
    RegistrationPermissionHandler,
)
from lego.apps.files.models import FileField
from lego.apps.followers.models import FollowEvent
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.constants import AUTUMN, PENALTY_TYPES, PENALTY_WEIGHTS, SPRING
from lego.apps.users.models import AbakusGroup, Membership, Penalty, User
from lego.utils.decorators import abakus_cached_property
from lego.utils.models import BasisModel
from lego.utils.youtube_validator import youtube_validator


class Event(Content, BasisModel, ObjectPermissionsModel):
    """
    An event has a type (e.g. Company presentation, Party. Eventually, each type of event might
    have slightly different 'requirements' or fields. For example, a company presentation will be
    connected to a company from our company database.

    An event has between 1 and X pools, each with their own capacity,
    to separate users based on groups. At `merge_time` all pools are combined into one.

    An event has a waiting list, filled with users who register after the event is full.
    """

    event_type = models.CharField(max_length=50, choices=constants.EVENT_TYPES)
    event_status_type = models.CharField(
        max_length=50, choices=constants.EVENT_STATUS_TYPES, default=constants.TBA
    )
    location = models.CharField(max_length=100)
    cover = FileField(related_name="event_covers")

    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    merge_time = models.DateTimeField(null=True)
    unregistration_deadline = models.DateTimeField(null=True)
    registration_deadline_hours = models.IntegerField(
        default=constants.REGISTRATION_CLOSE_TIME
    )
    unregistration_deadline_hours = models.IntegerField(
        default=constants.UNREGISTRATION_CLOSE_TIME
    )

    @property
    def registration_close_time(self) -> date:
        return self.start_time - timedelta(hours=self.registration_deadline_hours)

    @property
    def unregistration_close_time(self) -> date:
        return self.start_time - timedelta(hours=self.unregistration_deadline_hours)

    penalty_weight = models.PositiveIntegerField(default=1)
    penalty_weight_on_not_present = models.PositiveIntegerField(default=2)
    heed_penalties = models.BooleanField(default=True)
    company = models.ForeignKey(
        Company, related_name="events", null=True, on_delete=models.SET_NULL
    )
    responsible_group = models.ForeignKey(
        "users.AbakusGroup", on_delete=models.SET_NULL, null=True, related_name="events"
    )

    use_captcha = models.BooleanField(default=True)
    feedback_description = models.CharField(max_length=255, blank=True)
    feedback_required = models.BooleanField(default=False)
    is_priced = models.BooleanField(default=False)
    use_stripe = models.BooleanField(default=True)
    price_member = models.PositiveIntegerField(default=0)
    price_guest = models.PositiveIntegerField(default=0)
    payment_due_date = models.DateTimeField(null=True)
    payment_overdue_notified = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=True)
    use_consent = models.BooleanField(default=False)
    youtube_url = CharField(
        max_length=200, default="", validators=[youtube_validator], blank=True
    )
    legacy_registration_count = models.PositiveIntegerField(default=0)
    mazemap_poi = models.PositiveIntegerField(null=True)
    responsible_users = ManyToManyField(User)
    is_foreign_language = models.BooleanField(default=False, blank=False, null=False)
    show_company_description = models.BooleanField(
        default=False, blank=True, null=False
    )

    class Meta:
        permission_handler = EventPermissionHandler()
        indexes = [
            models.Index(fields=["end_time"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        By re-setting the pool counters on save, we can ensure that counters are updated if an
        event that has been merged gets un-merged. We want to avoid having to increment counters
        when registering after merge_time for performance reasons
        """
        with transaction.atomic():
            super().save(*args, **kwargs)
            for pool in self.pools.select_for_update().all():
                pool.counter = pool.registrations.count()
                pool.save(update_fields=["counter"])

        if self.pinned:
            for pinned_item in Event.objects.filter(pinned=True).exclude(pk=self.pk):
                pinned_item.pinned = False
                pinned_item.save()

    def user_should_see_regs(self, user: User) -> bool:
        return (
            self.get_possible_pools(user, future=True, is_admitted=False).exists()
            or user.is_abakom_member
            or (self.created_by is not None and self.created_by.id == user.id)
        )

    def user_should_see_allergies(self, user: User) -> bool:
        if user.is_anonymous:
            return False
        memberships = Membership.objects.filter(user=user)
        in_responsible_group = self.responsible_group in [
            mem.abakus_group for mem in memberships
        ]
        created_by_self = user == self.created_by
        in_responsible_users = self.responsible_users.filter(id=user.id).exists()
        return created_by_self or in_responsible_group or in_responsible_users

    def admin_register(
        self,
        admin_user: User,
        user: User,
        admin_registration_reason: str,
        pool: Optional[Pool] = None,
        feedback: str = "",
    ) -> Registration:
        """
        Used to force registration for a user, even if the event is full
        or if the user isn't allowed to register.

        :param user: The user who will be registered
        :param pool: What pool the registration will be created for
        :param feedback: Feedback to organizers
        :return: The registration
        """
        if pool and not self.pools.filter(id=pool.id).exists():
            raise NoSuchPool()
        with transaction.atomic():
            registration = self.registrations.get_or_create(event=self, user=user)[0]
            if registration.pool_id:
                raise RegistrationExists()

            if pool:
                locked_pool = Pool.objects.select_for_update().get(pk=pool.id)
                locked_pool.increment()

                registration.add_direct_to_pool(
                    pool,
                    feedback=feedback,
                    admin_registration_reason=admin_registration_reason,
                    created_by=admin_user,
                    updated_by=admin_user,
                )
            else:
                registration.add_to_waiting_list(
                    feedback=feedback,
                    admin_registration_reason=admin_registration_reason,
                    created_by=admin_user,
                    updated_by=admin_user,
                )
            # Make the user follow the event
            FollowEvent.objects.get_or_create(follower=user, target=self)
            handle_event(registration, "admin_registration")
            return registration

    def admin_unregister(
        self, admin_user: User, user: User, admin_unregistration_reason: str
    ) -> Registration:
        with transaction.atomic():
            registration: Optional[Registration] = self.registrations.filter(
                user=user
            ).first()
            if not registration:
                raise NoSuchRegistration()
            self.unregister(
                registration,
                admin_unregistration_reason=admin_unregistration_reason,
                updated_by=admin_user,
            )
            handle_event(registration, "admin_unregistration")
            return registration

    def get_absolute_url(self) -> str:
        return f"{settings.FRONTEND_URL}/events/{self.id}/"

    def can_register(
        self,
        user: User,
        pool: Pool,
        future: bool = False,
        is_admitted: Optional[bool] = None,
    ) -> bool:
        if not pool.is_activated and not future:
            return False

        if is_admitted is None:
            is_admitted = self.is_admitted(user)

        if is_admitted:
            return False

        for group in pool.permission_groups.all():
            if group in user.all_groups:
                return True
        return False

    def get_earliest_registration_time(
        self,
        user: User,
        pools: Optional[QuerySet[Pool] | list[Pool]] = None,
        penalties: Optional[int] = None,
    ) -> date | None:
        if pools is None:
            pools = self.get_possible_pools(user, future=True)
        if len(pools) == 0:
            return None
        reg_time: date = min(pool.activation_date for pool in pools)
        if self.heed_penalties:
            if penalties is None:
                penalties = user.number_of_penalties()
            if penalties == 2:
                return reg_time + timedelta(hours=12)
            elif penalties == 1:
                return reg_time + timedelta(hours=3)
        return reg_time

    def get_possible_pools(
        self,
        user: User,
        future: bool = False,
        all_pools: Optional[QuerySet[Pool]] = None,
        is_admitted: Optional[bool] = None,
    ) -> QuerySet[Pool]:
        if not all_pools:
            all_pools = self.pools.all()
        if is_admitted is None:
            is_admitted = self.is_admitted(user)
        if is_admitted:
            return Pool.objects.none()
        queryset: QuerySet[Pool] = all_pools.filter(
            permission_groups__in=user.all_groups
        ).distinct()
        if future:
            return queryset
        return queryset.filter(activation_date__lte=timezone.now())

    def register(self, registration: Registration) -> Registration:
        """
        Evaluates a pending registration for the event,
        and automatically selects the optimal pool for the registration.

        First checks if there exist any legal pools for the pending registration,
        raises an exception if not.

        If there is only one possible pool, checks if the pool is full and registers for
        the waiting list or the pool accordingly.

        If the event is merged, and it isn't full, joins any pool.
        Otherwise, joins the waiting list.

        If the event isn't merged, checks if the pools that the pending registration can
        possibly join are full or not. If all are full, a registration for
        the waiting list is created. If there's only one pool that isn't full,
        register for it.

        If there's more than one possible pool that isn't full,
        calculates the total amount of users that can join each pool, and selects the most
        exclusive pool. If several pools have the same exclusivity,
        selects the biggest pool of these.

        :param registration: The registration that gets evaluated
        :return: The registration (in the chosen pool)
        """
        user: User = registration.user
        penalties: int = 0

        unanswered_surveys = user.unanswered_surveys()
        if len(unanswered_surveys) > 0:
            raise UnansweredSurveyException()

        if self.heed_penalties:
            penalties = user.number_of_penalties()
        current_time = timezone.now()
        if self.registration_close_time < current_time:
            raise EventHasClosed()

        current_semester = AUTUMN if self.start_time.month > 7 else SPRING
        if self.use_consent and not user.has_registered_photo_consents_for_semester(
            self.start_time.year,
            current_semester,
        ):
            raise NotRegisteredPhotoConsents()

        all_pools: QuerySet[Pool] = self.pools.all()
        possible_pools = self.get_possible_pools(
            user, all_pools=all_pools, is_admitted=registration.is_admitted
        )
        if not self.is_ready:
            raise EventNotReady()
        if not possible_pools:
            raise ValueError("No available pools")
        earliest_reg: Optional[date] = self.get_earliest_registration_time(
            user, possible_pools, penalties
        )
        if earliest_reg and earliest_reg > current_time:
            raise ValueError("Not open yet")

        # Make the user follow the event
        FollowEvent.objects.get_or_create(follower=user, target=self)

        if penalties >= 3:
            return registration.add_to_waiting_list()

        # If the event is merged or has only one pool we can skip a lot of logic
        if all_pools.count() == 1:
            return registration.add_to_pool(possible_pools[0])

        if self.is_merged:
            with transaction.atomic():
                locked_event = Event.objects.select_for_update().get(pk=self.id)
                is_full = locked_event.is_full
                if not is_full:
                    return registration.add_direct_to_pool(possible_pools[0])
            return registration.add_to_waiting_list()

        # Calculates which pools that are full or open for registration based on capacity
        full_pools, open_pools = self.calculate_full_pools(possible_pools)

        if not open_pools:
            return registration.add_to_waiting_list()

        if len(open_pools) == 1:
            return registration.add_to_pool(open_pools[0])

        # Returns a list of the pool(s) with the least amount of potential members
        exclusive_pools: list[Pool] = self.find_most_exclusive_pools(open_pools)

        if len(exclusive_pools) == 1:
            chosen_pool = exclusive_pools[0]
        else:
            chosen_pool = self.select_highest_capacity(exclusive_pools)

        return registration.add_to_pool(chosen_pool)

    def unregister(
        self,
        registration: Registration,
        updated_by: Optional[User] = None,
        admin_unregistration_reason: str = "",
    ) -> None:
        """
        Pulls the registration, and clears relevant fields. Sets unregistration date.
        If the user was in a pool, and not in the waiting list,
        notifies the waiting list that there might be a bump available.
        """
        current_time = timezone.now()
        if self.unregistration_close_time < current_time:
            raise EventHasClosed()

        # Locks unregister so that no user can register before bump is executed.
        pool_id = registration.pool_id
        registration.unregister(
            is_merged=self.is_merged,
            admin_unregistration_reason=admin_unregistration_reason,
            updated_by=updated_by if updated_by is not None else registration.user,
        )
        if pool_id:
            if (
                not admin_unregistration_reason
                and self.heed_penalties
                and self.passed_unregistration_deadline
            ):
                if not registration.user.penalties.filter(source_event=self).exists():
                    Penalty.objects.create(
                        user=registration.user,
                        reason=f"Meldte seg av {self.title} for sent.",
                        weight=1,
                        source_event=self,
                    )

            with transaction.atomic():
                # This select_for_update will lock both the event row, and the pool
                # uregistered from. This makes sure that noone can register while we are bumping.
                locked_event = Event.objects.select_for_update().get(pk=self.id)
                locked_pool = locked_event.pools.select_for_update().get(id=pool_id)
                locked_event.check_for_bump_or_rebalance(locked_pool)
                follow_event_item = FollowEvent.objects.filter(
                    follower=registration.user, target=locked_event
                ).first()
                if follow_event_item:
                    follow_event_item.delete()

    def check_for_bump_or_rebalance(self, open_pool: Pool) -> None:
        """
        Checks if there is an available spot in the event.
        If so, and the event is merged, bumps the first person in the waiting list.
        If the event isn't merged, bumps the first user in
        the waiting list who is able to join `open_pool`.
        If no one is waiting for `open_pool`, check if anyone is waiting for
        any of the other pools and attempt to rebalance.

        NOTE: Remember to lock the event using select_for_update! AND lock the
        corresponding pools by including all pools in the select statement.

        :param open_pool: The pool where the unregistration happened.
        """
        if not self.is_full:
            if self.is_merged:
                self.bump()
            elif not open_pool.is_full:
                for registration in self.waiting_registrations:
                    if open_pool in self.get_possible_pools(registration.user):
                        return self.bump(to_pool=open_pool)
                self.try_to_rebalance(open_pool=open_pool)

    def bump(self, to_pool: Optional[Pool] = None) -> None:
        """
        Pops the appropriate registration from the waiting list,
        and moves the registration from the waiting list to `to pool`.

        :param to_pool: A pool with a free slot. If the event is merged, this will be null.
        """
        if self.waiting_registrations.exists():
            with transaction.atomic():
                first_waiting = self.pop_from_waiting_list(to_pool)
                if first_waiting:
                    new_pool: Optional[Pool] = None
                    if to_pool:
                        new_pool = to_pool
                        new_pool.increment()
                    else:
                        for pool in self.pools.select_for_update().all():
                            if self.can_register(first_waiting.user, pool):
                                new_pool = pool
                                new_pool.increment()
                                break
                    first_waiting.pool = new_pool
                    first_waiting.save(update_fields=["pool"])
                    handle_event(first_waiting, "bump")

    def early_bump(self, opening_pool: Pool) -> None:
        """
        Used when bumping users from waiting list to a pool that is about to be activated,
        using an async task. This is done to make sure these existing registrations are given
        the spot ahead of users that register at activation time.

        :param opening_pool: The pool about to be activated.
        """
        for reg in self.waiting_registrations:
            if opening_pool.is_full:
                break
            if self.heed_penalties and reg.user.number_of_penalties() >= 3:
                continue
            if self.can_register(reg.user, opening_pool, future=True):
                reg.pool = opening_pool
                reg.save()
                handle_event(reg, "bump")
        self.check_for_bump_or_rebalance(opening_pool)

    def bump_on_pool_creation_or_expansion(self) -> None:
        """
        Used when a pool's capacity is expanded or a new pool is created,
        so that waiting registrations are bumped before anyone else can fill
        the open spots. This is done on event update.

        This method does the same as `early_bump`, but only accepts people that can be bumped now,
        not people that can be bumped in the future.
        """
        open_pools: list[Pool] = [pool for pool in self.pools.all() if not pool.is_full]
        for pool in open_pools:
            for reg in self.waiting_registrations:
                if self.is_full or pool.is_full:
                    break
                if self.heed_penalties and reg.user.number_of_penalties() >= 3:
                    continue
                if self.can_register(reg.user, pool, future=True):
                    reg.pool = pool
                    reg.save()
                    handle_event(reg, "bump")
            self.check_for_bump_or_rebalance(pool)

    def try_to_rebalance(self, open_pool: Pool) -> None:
        """
        Pull the top waiting registrations for all pools, and try to
        move users in the pools they are waiting for to `open_pool` so
        that someone can be bumped.

        :param open_pool: The pool where the unregistration happened.
        """
        balanced_pools: list[Pool] = []
        bumped: bool = False

        for waiting_registration in self.waiting_registrations:
            for full_pool in self.get_possible_pools(waiting_registration.user):
                if full_pool not in balanced_pools:
                    balanced_pools.append(full_pool)
                    bumped = self.rebalance_pool(from_pool=full_pool, to_pool=open_pool)

                if bumped:
                    return

    def rebalance_pool(self, from_pool: Pool, to_pool: Pool) -> bool:
        """
        Iterates over registrations in a full pool, and checks
        if they can be moved to the open pool. If possible, moves
        a registration and calls `bump(from_pool)`.

        :param from_pool: A full pool with waiting registrations.
        :param to_pool: A pool with one open slot.
        :return: Boolean, whether or not `bump()` has been called.
        """
        to_pool_permissions = to_pool.permission_groups.all()
        bumped: bool = False
        for old_registration in self.registrations.filter(pool=from_pool):
            if to_pool.is_full:
                break
            moveable: bool = False
            user_groups = old_registration.user.all_groups
            for group in to_pool_permissions:
                if group in user_groups:
                    moveable = True
            if moveable:
                old_registration.pool = to_pool
                old_registration.save()
                self.bump(to_pool=from_pool)
                bumped = True
        return bumped

    def add_to_waiting_list(self, user: User) -> Registration:
        """
        Adds a user to the waiting list.

        :param user: The user that will be registered to the waiting list.
        :return: A registration for the waiting list, with `pool=null`
        """
        return self.registrations.update_or_create(
            event=self,
            user=user,
            defaults={
                "pool": None,
                "status": constants.SUCCESS_REGISTER,
                "unregistration_date": None,
            },
        )[0]

    def pop_from_waiting_list(
        self, to_pool: Optional[Pool] = None
    ) -> Registration | None:
        """
        Pops the first user in the waiting list that can join `to_pool`.
        If `from_pool=None`, pops the first user in the waiting list overall.

        :param to_pool: The pool we are bumping to. If post-merge, there is no pool.
        :return: The registration that is first in line for said pool.
        """

        if to_pool:
            for registration in self.waiting_registrations:
                if self.heed_penalties:
                    penalties: int = registration.user.number_of_penalties()
                    earliest_reg: Optional[date] = self.get_earliest_registration_time(
                        registration.user, [to_pool], penalties
                    )
                    if penalties < 3 and earliest_reg and earliest_reg < timezone.now():
                        if self.can_register(registration.user, to_pool):
                            return registration
                elif self.can_register(registration.user, to_pool):
                    return registration
            return None

        if self.heed_penalties:
            for registration in self.waiting_registrations:
                penalties = registration.user.number_of_penalties()
                earliest_reg = self.get_earliest_registration_time(
                    registration.user, None, penalties
                )
                if penalties < 3 and earliest_reg and earliest_reg < timezone.now():
                    return registration
            return None

        return self.waiting_registrations.first()

    @staticmethod
    def has_pool_permission(user: User, pool: Pool) -> bool:
        for group in pool.permission_groups.all():
            if group in user.all_groups:
                return True
        return False

    @staticmethod
    def calculate_full_pools(pools: QuerySet[Pool]) -> tuple[list[Pool], list[Pool]]:
        full_pools: list[Pool] = []
        open_pools: list[Pool] = []
        for pool in pools:
            if pool.is_full:
                full_pools.append(pool)
            else:
                open_pools.append(pool)
        return full_pools, open_pools

    @staticmethod
    def find_most_exclusive_pools(pools: list[Pool]) -> list[Pool]:
        lowest: float | int = float("inf")
        equal: list[Pool] = []
        for pool in pools:
            groups: QuerySet[AbakusGroup] = pool.permission_groups.all()
            users: int = sum(g.number_of_users for g in groups)
            if users == lowest:
                equal.append(pool)
            elif users < lowest:
                equal = [pool]
                lowest = users
        return equal

    @staticmethod
    def select_highest_capacity(pools: list[Pool]) -> Pool:
        capacities: list[int] = [pool.capacity for pool in pools]
        return pools[capacities.index(max(capacities))]

    def is_admitted(self, user: User) -> bool:
        if hasattr(self, "user_reg"):
            if len(self.user_reg) == 0:
                return False
            return self.user_reg[0].pool is not None
        return self.registrations.filter(user=user).exclude(pool=None).exists()

    def following(self, user: User) -> int | False:
        try:
            return FollowEvent.objects.get(follower=user, target=self).pk
        except FollowEvent.DoesNotExist:
            return False

    def is_on_waiting_list(self, user: User) -> bool:
        return self.registrations.filter(
            user=user, pool=None, status=constants.SUCCESS_REGISTER
        ).exists()

    def get_registration(self, user: User) -> Optional[Registration]:
        return self.registrations.filter(user=user).exclude(pool=None).first()

    def get_price(self, user: User) -> int:
        if user.is_authenticated and user.is_abakus_member:
            return self.price_member
        return self.price_guest

    def spots_left_for_user(self, user: User) -> int | None | Any:
        all_pools: QuerySet[Pool] = self.pools.all()
        pools: QuerySet[Pool] = self.get_possible_pools(user, all_pools=all_pools)
        if not pools:
            return None

        if self.is_merged:
            return all_pools.annotate(Count("registrations")).aggregate(
                spots_left=Sum("capacity") - Sum("registrations__count")
            )["spots_left"]

        return sum([pool.spots_left() for pool in pools])

    @property
    def is_merged(self) -> bool:
        if self.merge_time is None:
            return False
        return timezone.now() >= self.merge_time

    def get_is_full(self, queryset: Optional[QuerySet[Pool]] = None) -> bool:
        if queryset is None:
            queryset = self.pools.filter(activation_date__lte=timezone.now())
        query = queryset.annotate(Count("registrations")).aggregate(
            active_capacity=Sum("capacity"),
            registrations_count=Sum("registrations__count"),
        )
        active_capacity: int = query["active_capacity"] or 0
        registrations_count: int = query["registrations_count"] or 0
        if active_capacity == 0:
            return False
        return active_capacity <= registrations_count

    @property
    def is_full(self) -> bool:
        return self.get_is_full()

    @property
    def active_capacity(self) -> int:
        """Calculation capacity of pools that are active."""
        aggregate = (
            self.pools.all()
            .filter(activation_date__lte=timezone.now())
            .aggregate(Sum("capacity"))
        )
        return aggregate["capacity__sum"] or 0

    @property
    def total_capacity(self) -> int:
        """Prefetch friendly calculation of the total possible capacity of the event."""
        return sum([pool.capacity for pool in self.pools.all()])

    @property
    def registration_count(self) -> int:
        """Prefetch friendly counting of registrations for an event."""
        return sum(
            [pool.registrations.all().count() for pool in self.pools.all()],
            self.legacy_registration_count,
        )

    @property
    def number_of_registrations(self) -> int:
        """Registration count guaranteed not to include unregistered users."""
        return (
            self.registrations.filter(
                unregistration_date=None,
                status__in=[constants.SUCCESS_REGISTER, constants.FAILURE_UNREGISTER],
            )
            .exclude(pool=None)
            .count()
            + self.legacy_registration_count
        )

    @property
    def unregistered(self) -> QuerySet[Registration]:
        return self.registrations.filter(
            pool=None,
            unregistration_date__isnull=False,
            status=constants.SUCCESS_UNREGISTER,
        )

    @property
    def passed_unregistration_deadline(self) -> bool:
        if self.unregistration_deadline:
            return self.unregistration_deadline < timezone.now()
        return False

    @property
    def waiting_registrations(self) -> QuerySet[Registration]:
        return self.registrations.filter(
            pool=None,
            unregistration_date=None,
            status__in=[constants.SUCCESS_REGISTER, constants.FAILURE_UNREGISTER],
        )

    @property
    def waiting_registration_count(self) -> int:
        return self.waiting_registrations.count()

    def restricted_lookup(self) -> tuple[list[User], list]:
        """
        Restricted Mail
        """
        registrations: QuerySet[Registration] = self.registrations.filter(
            status=constants.SUCCESS_REGISTER
        )
        return [registration.user for registration in registrations], []

    def announcement_lookup(self, exclude_waiting_list: bool) -> list[User]:
        registrations: QuerySet[Registration] = self.registrations.filter(
            status=constants.SUCCESS_REGISTER
        )

        if exclude_waiting_list:
            registrations = registrations.exclude(pool=None)

        return [registration.user for registration in registrations]

    def add_legacy_registration(self) -> None:
        self.legacy_registration_count += 1
        self.save()


class Pool(BasisModel):
    """
    Pool which keeps track of users able to register from different grades/groups.
    """

    name = models.CharField(max_length=100)
    capacity = models.PositiveSmallIntegerField(default=0)
    event = models.ForeignKey(Event, related_name="pools", on_delete=models.CASCADE)
    activation_date = models.DateTimeField()
    permission_groups = models.ManyToManyField(AbakusGroup)

    counter = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["id"]

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        if not self.registrations.exists():
            return super().delete(*args, **kwargs)
        else:
            raise RegistrationsExistInPool("Registrations exist in Pool")

    @property
    def is_full(self) -> bool:
        if self.capacity == 0:
            return False
        return self.registrations.count() >= self.capacity

    def spots_left(self) -> int:
        return self.capacity - self.registrations.count()

    @property
    def is_activated(self) -> bool:
        return self.activation_date <= timezone.now()

    @property
    def registration_count(self) -> int:
        return self.registrations.count()

    def increment(self) -> Pool:
        self.counter += 1
        self.save(update_fields=["counter"])
        return self

    def decrement(self) -> Pool:
        self.counter -= 1
        self.save(update_fields=["counter"])
        return self

    @abakus_cached_property
    def all_permission_groups(self):
        groups = self.permission_groups.all()
        all_groups = set(groups)
        for group in groups:
            all_groups.update(group.get_descendants())
        return list(all_groups)

    def __str__(self) -> str:
        return self.name


class Registration(BasisModel):
    """
    A registration for an event. Can be connected to either a pool or a waiting list.
    """

    user = models.ForeignKey(
        User, related_name="registrations", on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event, related_name="registrations", on_delete=models.CASCADE
    )
    pool = models.ForeignKey(
        Pool, null=True, related_name="registrations", on_delete=models.CASCADE
    )
    registration_date = models.DateTimeField(db_index=True, null=True)
    unregistration_date = models.DateTimeField(null=True)
    feedback = models.CharField(max_length=255, blank=True)
    admin_registration_reason = models.CharField(max_length=255, blank=True)
    admin_unregistration_reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20, default=constants.PENDING_REGISTER, choices=constants.STATUSES
    )
    presence = models.CharField(
        max_length=20,
        default=constants.PRESENCE_CHOICES.UNKNOWN,
        choices=constants.PRESENCE_CHOICES.choices,
        db_index=True,
    )
    LEGACY_photo_consent = models.CharField(
        max_length=20,
        default=constants.UNKNOWN,
        choices=constants.LEGACY_PHOTO_CONSENT_CHOICES,
    )

    payment_intent_id = models.CharField(null=True, max_length=50)
    payment_amount = models.IntegerField(default=0)
    payment_amount_refunded = models.IntegerField(null=True, default=0)
    payment_status = models.CharField(null=True, max_length=50)
    last_notified_overdue_payment = models.DateTimeField(null=True)
    payment_idempotency_key = models.UUIDField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ["registration_date"]
        permission_handler = RegistrationPermissionHandler()
        indexes = [
            models.Index(fields=["status", "pool"]),
        ]

    def __str__(self) -> str:
        return str({"user": self.user, "pool": self.pool})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.validate()
        super().save(*args, **kwargs)

    @property
    def is_admitted(self) -> bool:
        return self.pool is not None

    @property
    def can_pay(self) -> bool:
        return self.is_admitted and self.event.is_priced and self.event.use_stripe

    def validate(self) -> None:
        if self.pool and self.unregistration_date:
            raise ValidationError("Pool and unregistration_date should not both be set")

    def has_paid(self) -> bool:
        return self.payment_status in [
            constants.PAYMENT_SUCCESS,
            constants.PAYMENT_MANUAL,
        ]

    def should_notify(self, time: Optional[datetime] = None) -> bool:
        if not time:
            time = timezone.now()
        if not self.has_paid():
            return (
                not self.last_notified_overdue_payment
                or (time - self.last_notified_overdue_payment).days
                >= constants.DAYS_BETWEEN_NOTIFY
            )
        return False

    def set_payment_success(self) -> Registration:
        self.payment_status = constants.PAYMENT_MANUAL
        self.save()
        return self

    def set_presence(self, presence: constants.PRESENCE_CHOICES) -> None:
        """Wrap this method in a transaction"""
        if presence not in constants.PRESENCE_CHOICES:
            raise ValueError("Illegal presence choice")

        self.presence = presence
        self.handle_user_penalty(presence)
        self.save()

    def delete_presence_penalties_for_event(self) -> None:
        for penalty in self.user.penalties.filter(
            source_event=self.event, type=PENALTY_TYPES.PRESENCE
        ):
            penalty.delete()

    def handle_user_penalty(self, presence: constants.PRESENCE_CHOICES) -> None:
        """
        Previous penalties related to the event are deleted since the
        newest presence is the only one that matters
        """

        if (
            self.event.heed_penalties
            and presence == constants.PRESENCE_CHOICES.NOT_PRESENT
            and self.event.penalty_weight_on_not_present
        ):
            self.delete_presence_penalties_for_event()
            Penalty.objects.create(
                user=self.user,
                reason=f"Møtte ikke opp på {self.event.title}.",
                weight=self.event.penalty_weight_on_not_present,
                source_event=self.event,
                type=PENALTY_TYPES.PRESENCE,
            )
        elif self.event.heed_penalties and presence == constants.PRESENCE_CHOICES.LATE:
            self.delete_presence_penalties_for_event()
            Penalty.objects.create(
                user=self.user,
                reason=f"Møtte for sent opp på {self.event.title}.",
                weight=PENALTY_WEIGHTS.LATE_PRESENCE,
                source_event=self.event,
                type=PENALTY_TYPES.PRESENCE,
            )
        else:
            self.delete_presence_penalties_for_event()

    def add_to_pool(self, pool: Pool) -> Registration:
        allowed: bool = False
        with transaction.atomic():
            locked_pool: Pool = Pool.objects.select_for_update().get(pk=pool.id)
            if locked_pool.capacity == 0 or locked_pool.counter < locked_pool.capacity:
                locked_pool.increment()
                allowed = True

        if allowed:
            return self.add_direct_to_pool(pool)
        return self.add_to_waiting_list()

    def add_direct_to_pool(self, pool: Pool, **kwargs: Any) -> Registration:
        return self.set_values(
            pool=pool,
            registration_date=timezone.now(),
            unregistration_date=None,
            status=constants.SUCCESS_REGISTER,
            **kwargs,
        )

    def add_to_waiting_list(self, **kwargs: Any) -> Registration:
        return self.set_values(
            pool=None,
            registration_date=timezone.now(),
            unregistration_date=None,
            status=constants.SUCCESS_REGISTER,
            **kwargs,
        )

    def unregister(
        self,
        is_merged: bool = False,
        updated_by: Optional[User] = None,
        admin_unregistration_reason: str = "",
    ) -> Registration:
        # Unfollow event
        followEvent = FollowEvent.objects.filter(
            follower=self.user, target=self.event
        ).first()
        if followEvent is not None:
            followEvent.delete()

        # We do not care about the counter if the event is merged or pool is None
        if self.pool and not is_merged:
            with transaction.atomic():
                locked_pool: Pool = Pool.objects.select_for_update().get(
                    pk=self.pool.id
                )
                locked_pool.decrement()
        return self.set_values(
            pool=None,
            unregistration_date=timezone.now(),
            status=constants.SUCCESS_UNREGISTER,
            admin_unregistration_reason=admin_unregistration_reason,
            updated_by=updated_by if updated_by is not None else self.user,
        )

    def set_values(self, **kwargs: Any) -> Registration:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save(update_fields=kwargs.keys())
        return self
