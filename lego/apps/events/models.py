from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Count, Sum
from django.utils import timezone

from lego.apps.companies.models import Company
from lego.apps.content.models import Content
from lego.apps.events import constants
from lego.apps.events.exceptions import (EventHasStarted, EventNotReady, NoSuchPool,
                                         RegistrationsExistInPool)
from lego.apps.events.permissions import EventPermissionHandler, RegistrationPermissionHandler
from lego.apps.feed.registry import get_handler
from lego.apps.files.models import FileField
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import AbakusGroup, Penalty, User
from lego.utils.models import BasisModel


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
    location = models.CharField(max_length=100)
    cover = FileField(related_name='event_covers')

    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    merge_time = models.DateTimeField(null=True)

    penalty_weight = models.PositiveIntegerField(default=1)
    penalty_weight_on_not_present = models.PositiveIntegerField(default=2)
    heed_penalties = models.BooleanField(default=True)
    company = models.ForeignKey(Company, related_name='events', null=True)

    use_captcha = models.BooleanField(default=True)
    feedback_description = models.CharField(max_length=255, blank=True)
    feedback_required = models.BooleanField(default=False)
    is_priced = models.BooleanField(default=False)
    use_stripe = models.BooleanField(default=True)
    price_member = models.PositiveIntegerField(default=0)
    price_guest = models.PositiveIntegerField(default=0)
    payment_due_days = models.PositiveSmallIntegerField(null=True)
    payment_overdue_notified = models.BooleanField(default=False)

    is_ready = models.BooleanField(default=True)

    class Meta:
        permission_handler = EventPermissionHandler()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        By re-setting the pool counters on save, we can ensure that counters are updated if an
        event that has been merged gets un-merged. We want to avoid having to increment counters
        when registering after merge_time for performance reasons
        """
        with transaction.atomic():
            for pool in self.pools.select_for_update().all():
                pool.counter = pool.registrations.count()
                pool.save(update_fields=['counter'])
            return super().save(*args, **kwargs)

    def admin_register(self, user, pool, admin_reason, feedback=''):
        """
        Used to force registration for a user, even if the event is full
        or if the user isn't allowed to register.

        :param user: The user who will be registered
        :param pool: What pool the registration will be created for
        :param feedback: Feedback to organizers
        :return: The registration
        """
        if self.pools.filter(id=pool.id).exists():
            with transaction.atomic():
                reg = self.registrations.update_or_create(
                    event=self,
                    user=user,
                    defaults={'pool': pool,
                              'feedback': feedback,
                              'registration_date': timezone.now(),
                              'unregistration_date': None,
                              'status': constants.SUCCESS_REGISTER,
                              'admin_reason': admin_reason}
                )[0]
                locked_pool = Pool.objects.select_for_update().get(pk=pool.id)
                locked_pool.increment()

                get_handler(Registration).handle_admin_registration(reg)
                return reg
        else:
            raise NoSuchPool()

    def get_absolute_url(self):
        return f'{settings.FRONTEND_URL}/events/{self.id}/'

    def can_register(self, user, pool, future=False, is_registered=None):
        if not pool.is_activated and not future:
            return False

        if is_registered is None:
            is_registered = self.is_registered(user)

        if is_registered:
            return False

        for group in pool.permission_groups.all():
            if group in user.all_groups:
                return True
        return False

    def get_earliest_registration_time(self, user, pools=None, penalties=None):

        if not pools:
            pools = self.get_possible_pools(user, future=True)
            if not pools:
                return None
        reg_time = min(pool.activation_date for pool in pools)
        if self.heed_penalties:
            if not penalties:
                penalties = user.number_of_penalties()
            if penalties == 2:
                return reg_time + timedelta(hours=12)
            elif penalties == 1:
                return reg_time + timedelta(hours=3)
        return reg_time

    def get_possible_pools(self, user, future=False, all_pools=None, is_registered=None):
        if not all_pools:
            all_pools = self.pools.all()
        if is_registered is None:
            is_registered = self.is_registered(user)
        if is_registered:
            return []
        queryset = all_pools.filter(permission_groups__in=user.all_groups)
        if future:
            return queryset
        return queryset.filter(activation_date__lte=timezone.now())

    def register(self, registration):
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
        user = registration.user
        penalties = None
        if self.heed_penalties:
            penalties = user.number_of_penalties()
        current_time = timezone.now()
        if self.start_time < current_time:
            raise EventHasStarted()

        all_pools = self.pools.all()
        possible_pools = self.get_possible_pools(
            user, all_pools=all_pools, is_registered=registration.is_registered
        )
        if not self.is_ready:
            raise EventNotReady()
        if not possible_pools:
            raise ValueError('No available pools')
        if self.get_earliest_registration_time(user, possible_pools, penalties) > current_time:
            raise ValueError('Not open yet')

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
        exclusive_pools = self.find_most_exclusive_pools(open_pools)

        if len(exclusive_pools) == 1:
            chosen_pool = exclusive_pools[0]
        else:
            chosen_pool = self.select_highest_capacity(exclusive_pools)

        return registration.add_to_pool(chosen_pool)

    def unregister(self, registration):
        """
        Pulls the registration, and clears relevant fields. Sets unregistration date.
        If the user was in a pool, and not in the waiting list,
        notifies the waiting list that there might be a bump available.
        """
        if self.start_time < timezone.now():
            raise EventHasStarted()

        # Locks unregister so that no user can register before bump is executed.
        pool = registration.pool
        registration.unregister(is_merged=self.is_merged)
        if pool:
            if self.heed_penalties and pool.passed_unregistration_deadline():
                if not registration.user.penalties.filter(source_event=self).exists():
                    Penalty.objects.create(
                        user=registration.user,
                        reason='Unregistered from event too late',
                        weight=1, source_event=self
                    )
            with transaction.atomic():
                locked_event = Event.objects.select_for_update().get(pk=self.id)
                locked_event.check_for_bump_or_rebalance(pool)

    def check_for_bump_or_rebalance(self, open_pool):
        """
        Checks if there is an available spot in the event.
        If so, and the event is merged, bumps the first person in the waiting list.
        If the event isn't merged, bumps the first user in
        the waiting list who is able to join `open_pool`.
        If no one is waiting for `open_pool`, check if anyone is waiting for
        any of the other pools and attempt to rebalance.

        NOTE: Remember to lock the event using select_for_update!

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

    def bump(self, to_pool=None):
        """
        Pops the appropriate registration from the waiting list,
        and moves the registration from the waiting list to `to pool`.

        :param to_pool: A pool with a free slot. If the event is merged, this will be null.
        """
        if self.waiting_registrations.exists():
            first_waiting = self.pop_from_waiting_list(to_pool)
            if first_waiting:
                new_pool = None
                if to_pool:
                    new_pool = to_pool
                    new_pool.increment()
                else:
                    for pool in self.pools.all():
                        if self.can_register(first_waiting.user, pool):
                            new_pool = pool
                            new_pool.increment()
                            break
                first_waiting.pool = new_pool
                first_waiting.save(update_fields=['pool'])
                get_handler(Registration).handle_bump(first_waiting)

    def early_bump(self, opening_pool):
        """
        Used when bumping users from waiting list to a pool that is about to be activated,
        using an async task. This is done to make sure these existing registrations are given
        the spot ahead of users that register at activation time.
        :param opening_pool: The pool about to be activated.
        :return:
        """
        for reg in self.waiting_registrations:
            if opening_pool.is_full:
                break
            if self.heed_penalties and reg.user.number_of_penalties() >= 3:
                continue
            if self.can_register(reg.user, opening_pool, future=True):
                reg.pool = opening_pool
                reg.save()
                get_handler(Registration).handle_bump(reg)
        self.check_for_bump_or_rebalance(opening_pool)

    def bump_on_pool_creation_or_expansion(self):
        """
        Used when a pool's capacity is expanded or a new pool is created,
        so that waiting registrations are bumped before anyone else can fill
        the open spots. This is done on event update.

        This method does the same as `early_bump`, but only accepts people that can be bumped now,
        not people that can be bumped in the future.
        :return:
        """
        open_pools = [pool for pool in self.pools.all() if not pool.is_full]
        for pool in open_pools:
            for reg in self.waiting_registrations:
                if pool.is_full:
                    break
                if self.heed_penalties and reg.user.number_of_penalties() >= 3:
                    continue
                if self.can_register(reg.user, pool, future=True):
                    reg.pool = pool
                    reg.save()
                    get_handler(Registration).handle_bump(reg)
            self.check_for_bump_or_rebalance(pool)

    def try_to_rebalance(self, open_pool):
        """
        Pull the top waiting registrations for all pools, and try to
        move users in the pools they are waiting for to `open_pool` so
        that someone can be bumped.

        :param open_pool: The pool where the unregistration happened.
        """
        balanced_pools = []
        bumped = False

        for waiting_registration in self.waiting_registrations:
            for full_pool in self.get_possible_pools(waiting_registration.user):

                if full_pool not in balanced_pools:
                    balanced_pools.append(full_pool)
                    bumped = self.rebalance_pool(from_pool=full_pool, to_pool=open_pool)

                if bumped:
                    return

    def rebalance_pool(self, from_pool, to_pool):
        """
        Iterates over registrations in a full pool, and checks
        if they can be moved to the open pool. If possible, moves
        a registration and calls `bump(from_pool)`.

        :param from_pool: A full pool with waiting registrations.
        :param to_pool: A pool with one open slot.
        :return: Boolean, whether or not `bump()` has been called.
        """
        to_pool_permissions = to_pool.permission_groups.all()
        bumped = False
        for old_registration in self.registrations.filter(pool=from_pool):
            moveable = False
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

    def add_to_waiting_list(self, user):
        """
        Adds a user to the waiting list.

        :param user: The user that will be registered to the waiting list.
        :return: A registration for the waiting list, with `pool=null`
        """
        return self.registrations.update_or_create(event=self, user=user,
                                                   defaults={'pool': None,
                                                             'unregistration_date': None})[0]

    def pop_from_waiting_list(self, to_pool=None):
        """
        Pops the first user in the waiting list that can join `to_pool`.
        If `from_pool=None`, pops the first user in the waiting list overall.

        :param to_pool: The pool we are bumping to. If post-merge, there is no pool.
        :return: The registration that is first in line for said pool.
        """

        if to_pool:
            permission_groups = to_pool.permission_groups.all()
            for registration in self.waiting_registrations:
                penalties = None
                earliest_reg = None
                if self.heed_penalties:
                    penalties = registration.user.number_of_penalties()
                    earliest_reg = self.get_earliest_registration_time(
                                 registration.user, [to_pool], penalties
                    )
                if self.heed_penalties and penalties < 3 and earliest_reg < timezone.now():
                    for group in registration.user.all_groups:
                        if group in permission_groups:
                            return registration
            return None

        if self.heed_penalties:
            for registration in self.waiting_registrations:
                penalties = registration.user.number_of_penalties()
                earliest_reg = self.get_earliest_registration_time(
                             registration.user, None, penalties
                )
                if penalties < 3 and earliest_reg < timezone.now():
                    return registration
            return None

        return self.waiting_registrations.first()

    @staticmethod
    def has_pool_permission(user, pool):
        for group in pool.permission_groups.all():
            if group in user.all_groups:
                return True
        return False

    @staticmethod
    def calculate_full_pools(pools):
        full_pools = []
        open_pools = []
        for pool in pools:
            if pool.is_full:
                full_pools.append(pool)
            else:
                open_pools.append(pool)
        return full_pools, open_pools

    @staticmethod
    def find_most_exclusive_pools(pools):
        lowest = float('inf')
        equal = []
        for pool in pools:
            groups = pool.permission_groups.all()
            users = sum(g.number_of_users for g in groups)
            if users == lowest:
                equal.append(pool)
            elif users < lowest:
                equal = [pool]
                lowest = users
        return equal

    @staticmethod
    def select_highest_capacity(pools):
        capacities = [pool.capacity for pool in pools]
        return pools[capacities.index(max(capacities))]

    def is_registered(self, user):
        return self.registrations.filter(user=user).exclude(pool=None).exists()

    def get_registration(self, user):
        return self.registrations.filter(user=user).exclude(pool=None).first()

    def get_price(self, user):
        if user.is_abakus_member:
            return self.price_member
        return self.price_guest

    def spots_left_for_user(self, user):

        all_pools = self.pools.all()
        pools = self.get_possible_pools(user, all_pools=all_pools)
        if not pools:
            return None

        if self.is_merged:
            return all_pools.annotate(Count('registrations'))\
                .aggregate(spots_left=Sum('capacity') - Sum('registrations__count'))['spots_left']

        return sum([pool.spots_left() for pool in pools])

    @property
    def is_merged(self):
        if self.merge_time is None:
            return False
        return timezone.now() >= self.merge_time

    def get_is_full(self, queryset=None):
        if queryset is None:
            queryset = self.pools.filter(activation_date__lte=timezone.now())
        query = queryset.annotate(Count('registrations')).aggregate(
            active_capacity=Sum('capacity'), registrations_count=Sum('registrations__count')
        )
        active_capacity = query['active_capacity'] or 0
        registrations_count = query['registrations_count'] or 0
        if active_capacity == 0:
            return False
        return active_capacity <= registrations_count

    @property
    def is_full(self):
        return self.get_is_full()

    @property
    def active_capacity(self):
        """ Calculation capacity of pools that are active. """
        aggregate = self.pools.all().filter(activation_date__lte=timezone.now())\
            .aggregate(Sum('capacity'))
        return aggregate['capacity__sum'] or 0

    @property
    def total_capacity(self):
        """ Prefetch friendly calculation of the total possible capacity of the event. """
        return sum([pool.capacity for pool in self.pools.all()])

    @property
    def registration_count(self):
        """ Prefetch friendly counting of registrations for an event. """
        return sum([pool.registrations.all().count() for pool in self.pools.all()])

    @property
    def number_of_registrations(self):
        """ Registration count guaranteed not to include unregistered users. """
        return self.registrations.filter(
            unregistration_date=None,
            status__in=[constants.SUCCESS_REGISTER, constants.FAILURE_UNREGISTER]
        ).exclude(pool=None).count()

    @property
    def unregistered(self):
        return self.registrations.filter(
            pool=None,
            unregistration_date__isnull=False,
            status=constants.SUCCESS_UNREGISTER
        )

    @property
    def waiting_registrations(self):
        return self.registrations.filter(
            pool=None,
            unregistration_date=None,
            status__in=[constants.SUCCESS_REGISTER, constants.FAILURE_UNREGISTER]
        )

    def restricted_lookup(self):
        """
        Restricted Mail
        """
        registrations = self.registrations.filter(status=constants.SUCCESS_REGISTER)
        return [registration.user for registration in registrations], []

    def announcement_lookup(self):
        registrations = self.registrations.filter(status=constants.SUCCESS_REGISTER)
        return [registration.user for registration in registrations]


class Pool(BasisModel):
    """
    Pool which keeps track of users able to register from different grades/groups.
    """

    name = models.CharField(max_length=100)
    capacity = models.PositiveSmallIntegerField(default=0)
    event = models.ForeignKey(Event, related_name='pools')
    activation_date = models.DateTimeField()
    unregistration_deadline = models.DateTimeField(null=True)
    permission_groups = models.ManyToManyField(AbakusGroup)

    counter = models.PositiveSmallIntegerField(default=0)

    def delete(self, *args, **kwargs):
        if not self.registrations.exists():
            super().delete(*args, **kwargs)
        else:
            raise RegistrationsExistInPool('Registrations exist in Pool')

    @property
    def is_full(self):
        if self.capacity == 0:
            return False
        return self.registrations.count() >= self.capacity

    def spots_left(self):
        return self.capacity - self.registrations.count()

    @property
    def is_activated(self):
        return self.activation_date <= timezone.now()

    def increment(self):
        self.counter += 1
        self.save(update_fields=['counter'])
        return self

    def decrement(self):
        self.counter -= 1
        self.save(update_fields=['counter'])
        return self

    def passed_unregistration_deadline(self):
        if self.unregistration_deadline:
            return self.unregistration_deadline < timezone.now()
        return False

    def __str__(self):
        return self.name


class Registration(BasisModel):
    """
    A registration for an event. Can be connected to either a pool or a waiting list.
    """
    user = models.ForeignKey(User, related_name='registrations')
    event = models.ForeignKey(Event, related_name='registrations')
    pool = models.ForeignKey(Pool, null=True, related_name='registrations')
    registration_date = models.DateTimeField(db_index=True, null=True)
    unregistration_date = models.DateTimeField(null=True)
    feedback = models.CharField(max_length=255, blank=True)
    admin_reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20, default=constants.PENDING_REGISTER, choices=constants.STATUSES
    )
    presence = models.CharField(
        max_length=20, default=constants.UNKNOWN, choices=constants.PRESENCE_CHOICES
    )

    charge_id = models.CharField(null=True, max_length=50)
    charge_amount = models.IntegerField(default=0)
    charge_amount_refunded = models.IntegerField(default=0)
    charge_status = models.CharField(null=True, max_length=50)
    last_notified_overdue_payment = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['registration_date']
        permission_handler = RegistrationPermissionHandler()

    def __str__(self):
        return str({"user": self.user, "pool": self.pool})

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)

    @property
    def is_registered(self):
        return self.pool is not None

    def is_registration_due_payment(self):
        if not self.is_registered or self.has_paid():
            return False
        return self.registration_date + timedelta(days=self.event.payment_due_days) > timezone.now()

    def validate(self):
        if self.pool and self.unregistration_date:
            raise ValidationError('Pool and unregistration_date should not both be set')

    def has_paid(self):
        return self.charge_status in [constants.PAYMENT_SUCCESS, constants.PAYMENT_MANUAL]

    def should_notify(self, time=None):
        if not time:
            time = timezone.now()
        if self.is_registration_due_payment():
            return not self.last_notified_overdue_payment or\
               (time - self.last_notified_overdue_payment).days >= constants.DAYS_BETWEEN_NOTIFY
        return False

    def set_payment_success(self):
        self.charge_status = constants.PAYMENT_MANUAL
        self.save()
        return self

    def set_presence(self, presence):
        """Wrap this method in a transaction"""
        if presence not in dict(constants.PRESENCE_CHOICES):
            raise ValueError('Illegal presence choice')
        self.presence = presence
        self.handle_user_penalty(presence)
        self.save()

    def handle_user_penalty(self, presence):
        if presence == constants.NOT_PRESENT and self.event.penalty_weight_on_not_present:
            if not self.user.penalties.filter(source_event=self.event).exists():
                Penalty.objects.create(
                    user=self.user,
                    reason=f'was registered to event {self.event.title}, but did not attend it.',
                    weight=self.event.penalty_weight_on_not_present, source_event=self.event
                )
        else:
            for penalty in self.user.penalties.filter(source_event=self.event):
                penalty.delete()

    def add_to_pool(self, pool):
        allowed = False
        with transaction.atomic():
            locked_pool = Pool.objects.select_for_update().get(pk=pool.id)
            if locked_pool.capacity == 0 or locked_pool.counter < locked_pool.capacity:
                locked_pool.increment()
                allowed = True

        if allowed:
            return self.add_direct_to_pool(pool)
        return self.add_to_waiting_list()

    def add_direct_to_pool(self, pool):
        self.registration_date = timezone.now()
        return self.set_values(pool, None, constants.SUCCESS_REGISTER)

    def add_to_waiting_list(self):
        self.registration_date = timezone.now()
        return self.set_values(None, None, constants.SUCCESS_REGISTER)

    def unregister(self, is_merged=None):
        # We do not care about the counter if the event is merged or pool is None
        if self.pool and not is_merged:
            with transaction.atomic():
                locked_pool = Pool.objects.select_for_update().get(pk=self.pool.id)
                locked_pool.decrement()
        return self.set_values(None, timezone.now(), constants.SUCCESS_UNREGISTER)

    def set_values(self, pool, unregistration_date, status):
        self.pool = pool
        self.unregistration_date = unregistration_date
        self.status = status
        self.save(update_fields=['registration_date', 'pool', 'unregistration_date', 'status'])
        return self
