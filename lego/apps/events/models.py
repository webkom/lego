from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from lego.apps.content.models import SlugContent
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import AbakusGroup, User
from lego.utils.models import BasisModel

from .exceptions import NoAvailablePools, UserNotAdmin


class Event(SlugContent, BasisModel, ObjectPermissionsModel):
    """
    An event has a type (e.g. Company presentation, Party. Eventually, each type of event might
    have slightly different 'requirements' or fields. For example, a company presentation will be
    connected to a company from our company database.

    An event has between 1 and X pools, each with their own capacity,
    to separate users based on groups. At `merge_time` all pools are combined into one.

    An event has a waiting list, filled with users who register after the event is full.
    """

    COMPANY_PRESENTATION = 0
    COURSE = 1
    PARTY = 2
    OTHER = 3
    EVENT = 4

    EVENT_TYPES = (
        (COMPANY_PRESENTATION, _('Company presentation')),
        (COURSE, _('Course')),
        (PARTY, _('Party')),
        (OTHER, _('Other')),
        (EVENT, _('Event'))
    )

    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPES)
    location = models.CharField(max_length=100)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    merge_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return self.title

    def can_register(self, user, pool):
        if not self.is_activated(pool):
            return False

        if self.is_registered(user):
            return False

        for group in pool.permission_groups.all():
            if group in user.all_groups:
                return True
        return False

    def admin_register(self, request_user, user, pool):
        """
        Currently incomplete. Used to force registration for a user, even if the event is full
        or if the user isn't allowed to register.

        :param request_user: The user who forces the registration. Has to be an admin.
        :param user: The user who will be registered
        :param pool: What pool the registration will be created for
        :return: The registration
        """
        if self.can_edit(request_user):
            if pool in self.pools.all():
                return \
                    self.registrations.update_or_create(event=self, user=user,
                                                        defaults={'pool': pool,
                                                                  'unregistration_date': None})[0]
            else:
                raise ValueError('No such pool in this event')
        else:
            raise UserNotAdmin()

    def add_to_waiting_list(self, user):
        """
        Adds a user to the waiting list.

        :param user: The user that will be registered to the waiting list.
        :return: A registration for the waiting list, with `pool=null`
        """
        return self.registrations.get_or_create(event=self, user=user)[0]

    def pop_from_waiting_list(self, to_pool=None):
        """
        Pops the first user in the waiting list that can join `to_pool`.
        If `from_pool=None`, pops the first user in the waiting list overall.

        :param from_pool: The pool we are bumping to. If post-merge, there is no pool.
        :return: The registration that is first in line for said pool.
        """
        if to_pool:
            permission_groups = to_pool.permission_groups.all()
            for registration in self.waiting_registrations:
                for group in registration.user.all_groups:
                    if group in permission_groups:
                        return registration
        return self.waiting_registrations.first()

    def get_possible_pools(self, user):
        return [pool for pool in self.pools.all() if self.can_register(user, pool)]

    def register(self, user):
        """
        Creates a registration for the event,
        and automatically selects the optimal pool for the user.

        First checks if the user can register at all, raises an exception if not.

        If there is only one possible pool, checks if the pool is full and registers for
        the waiting list or the pool accordingly.

        If the event is merged, and it isn't full, joins any pool.
        Otherwise, joins the waiting list.

        If the event isn't merged, checks if the pools that the user can
        possibly join are full or not. If all are full, a registration for
        the waiting list is created. If there's only one pool that isn't full,
        register for it.

        If there's more than one possible pool that isn't full,
        calculates the total amount of users that can join each pool, and selects the most
        exclusive pool. If several pools have the same exclusivity,
        selects the biggest pool of these.

        :param user: The user who is trying to register
        :return: The registration (in the chosen pool)
        """

        possible_pools = self.get_possible_pools(user)
        if not possible_pools:
            raise NoAvailablePools()

        # If the event is merged or has only one pool we can skip a lot of logic
        if self.is_merged or (len(possible_pools) == 1 and self.pools.count() == 1):
            if self.is_full:
                return self.add_to_waiting_list(user=user)

            return self.registrations.update_or_create(event=self, user=user,
                                                       defaults={'pool': possible_pools[0],
                                                                 'unregistration_date': None})[0]

        # Calculates which pools that are full or open for registration based on capacity
        full_pools, open_pools = self.calculate_full_pools(possible_pools)

        if not open_pools:
            return self.add_to_waiting_list(user=user)

        elif len(open_pools) == 1:
            return self.registrations.update_or_create(event=self, user=user,
                                                       defaults={'pool': open_pools[0],
                                                                 'unregistration_date': None})[0]

        else:
            # Returns a list of the pool(s) with the least amount of potential members
            exclusive_pools = self.find_most_exclusive_pools(open_pools)

            if len(exclusive_pools) == 1:
                chosen_pool = exclusive_pools[0]
            else:
                chosen_pool = self.select_highest_capacity(exclusive_pools)

            return self.registrations.update_or_create(event=self, user=user,
                                                       defaults={'pool': chosen_pool,
                                                                 'unregistration_date': None})[0]

    def unregister(self, user):
        """
        Pulls the registration, and clears relevant fields. Sets unregistration date.
        If the user was in a pool, and not in the waiting list,
        notifies the waiting list that there might be a bump available.
        """
        registration = self.registrations.get(user=user)
        pool = registration.pool
        registration.pool = None
        registration.unregistration_date = timezone.now()
        registration.save()
        if pool:
            self.check_for_bump_or_rebalance(pool)

    def check_for_bump_or_rebalance(self, open_pool):
        """
        Checks if there is an available spot in the event.
        If so, and the event is merged, bumps the first person in the waiting list.
        If the event isn't merged, bumps the first user in
        the waiting list who is able to join `open_pool`.
        If no one is waiting for `open_pool`, check if anyone is waiting for
        any of the other pools and attempt to rebalance.

        :param open_pool: The pool where the unregistration happened.
        """
        if self.number_of_registrations < self.capacity:
            if self.is_merged:
                self.bump()
            else:
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
            top = self.pop_from_waiting_list(to_pool)
            if to_pool:
                top.pool = to_pool
            else:
                for pool in self.pools.all():
                    if self.can_register(top.user, pool):
                        top.pool = pool
                        break
            top.unregistration_date = None
            top.save()

    def is_activated(self, pool):
        return pool.activation_date <= timezone.now()

    def is_registered(self, user):
        return self.registrations.filter(user=user).exclude(pool=None).exists()

    @property
    def is_merged(self):
        if self.merge_time is None:
            return False
        return timezone.now() >= self.merge_time

    @property
    def is_full(self):
        return self.capacity <= self.number_of_registrations

    def has_pool_permission(self, user, pool):
        for group in pool.permission_groups.all():
            if group in user.all_groups:
                return True
        return False

    @property
    def capacity(self):
        aggregate = self.pools.all().filter(activation_date__lte=timezone.now())\
            .aggregate(Sum('capacity'))
        return aggregate['capacity__sum'] or 0

    @property
    def number_of_registrations(self):
        return self.registrations.filter(unregistration_date=None).exclude(pool=None).count()

    @property
    def waiting_registrations(self):
        return self.registrations.filter(pool=None, unregistration_date=None)

    def calculate_full_pools(self, pools):
        full_pools = []
        open_pools = []
        for pool in pools:
            if pool.is_full:
                full_pools.append(pool)
            else:
                open_pools.append(pool)
        return full_pools, open_pools

    def find_most_exclusive_pools(self, pools):
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

    def select_highest_capacity(self, pools):
        capacities = [pool.capacity for pool in pools]
        return pools[capacities.index(max(capacities))]

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


class Pool(BasisModel):
    """
    Pool which keeps track of users able to register from different grades/groups.
    """

    name = models.CharField(max_length=100)
    capacity = models.PositiveSmallIntegerField(default=0)
    event = models.ForeignKey(Event, related_name='pools')
    activation_date = models.DateTimeField()
    permission_groups = models.ManyToManyField(AbakusGroup)

    def delete(self, *args, **kwargs):
        if not self.registrations.exists():
            super().delete(*args, **kwargs)
        else:
            raise ValueError('Registrations exist in Pool')

    @property
    def is_full(self):
        return self.registrations.count() >= self.capacity

    def __str__(self):
        return self.name


class Registration(BasisModel):
    """
    A registration for an event. Can be connected to either a pool or a waiting list.
    """
    user = models.ForeignKey(User, related_name='registrations')
    event = models.ForeignKey(Event, related_name='registrations')
    pool = models.ForeignKey(Pool, null=True, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    unregistration_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['registration_date']

    def __str__(self):
        return str({"user": self.user, "pool": self.pool})
