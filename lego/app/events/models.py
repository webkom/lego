from basis.models import BasisModel
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from lego.app.content.models import Content
from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import AbakusGroup, User

from .exceptions import NoAvailablePools


class Event(Content, BasisModel, ObjectPermissionsModel):
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        WaitingList.objects.get_or_create(event=self)

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
        return self.registrations.create(event=self, user=user, pool=pool)

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

        possible_pools = [pool
                          for pool in self.all_pools
                          if self.can_register(user, pool)]
        if not possible_pools:
            raise NoAvailablePools()

        # If there's only one pool we can skip a lot of logic
        if len(possible_pools) == 1 and self.number_of_pools == 1:

            if possible_pools[0].is_full:
                return self.waiting_list.add(user=user, pools=possible_pools)
            else:
                return self.registrations.create(event=self, user=user, pool=possible_pools[0])

        # If the event is merged we can skip a lot of logic
        if self.is_merged:
            if self.is_full:
                return self.waiting_list.add(user=user, pools=possible_pools)
            else:
                return self.registrations.create(event=self, user=user, pool=possible_pools[0])
        else:
            full_pools = self.calculate_and_pop_full_pools(possible_pools)

            if not possible_pools:
                return self.waiting_list.add(user=user, pools=full_pools)

            if len(possible_pools) == 1:
                return self.registrations.create(event=self, user=user, pool=possible_pools[0])

        # Returns a dictionary where key = pool and value = potential members
        potential_members = self.calculate_potential_members(possible_pools)

        # Returns a list of the pool(s) with the least amount of potential members
        exclusive_pools = self.find_most_exclusive_pools(potential_members)

        if len(exclusive_pools) == 1:
            chosen_pool = exclusive_pools[0]
        else:
            chosen_pool = self.select_highest_capacity(exclusive_pools)

        return self.registrations.create(event=self, user=user, pool=chosen_pool)

    def unregister(self, user):
        """
        Pulls the registration, and clears relevant fields. Sets unregistration date.
        If the user was in a pool, and not in the waiting list,
        notifies the waiting list that there might be a bump available.
        """
        registration = self.registrations.get(user=user)
        pool = registration.pool
        registration.pool = None
        registration.waiting_list = None
        registration.waiting_pool.clear()
        registration.unregistration_date = timezone.now()
        registration.save()
        if pool:
            self.check_for_bump(pool)

    def check_for_bump(self, pool):
        """
        Checks if there is an available spot in the event.
        If so, and the event is merged, bumps the first person in the waiting list.
        If the event isn't merged, bumps the first user in
        the waiting list who is able to join `pool`.

        :param pool: The pool where the unregistration happened.
        """
        if self.number_of_registrations < self.capacity:
            if self.is_merged:
                self.bump()
            elif pool.waiting_registrations.count() > 0:
                self.bump(from_pool=pool)

    def bump(self, from_pool=None):
        """
        Pops the appropriate user/registration from the waiting list,
        and alters his registration to put him in a pool.

        :param from_pool: A pool with a free slot. If the event is merged, this will be null.
        """
        if self.waiting_list.number_of_registrations > 0:
            top = self.waiting_list.pop(from_pool=from_pool)
            if from_pool:
                pool = top.waiting_pool.filter(id=from_pool.id)
                top.pool = pool[0]
            else:
                top.pool = top.waiting_pool.first()
            top.waiting_pool.clear()
            top.unregistration_date = None
            top.save()

    def is_activated(self, pool):
        return pool.activation_date <= timezone.now()

    @property
    def is_merged(self):
        if self.merge_time is None:
            return True
        if self.number_of_pools > 1:
            return timezone.now() >= self.merge_time

    @property
    def is_full(self):
        return self.capacity <= self.number_of_registrations

    def is_registered(self, user):
        return self.registrations.filter(user=user).exists()

    @property
    def capacity(self):
        aggregate = self.all_pools.filter(activation_date__lte=timezone.now())\
            .aggregate(Sum('capacity'))
        return aggregate['capacity__sum'] or 0

    @property
    def number_of_registrations(self):
        return self.registrations.filter(waiting_list=None, waiting_pool=None,
                                         unregistration_date=None).count()

    @property
    def number_of_waiting_registrations(self):
        return self.waiting_list.number_of_registrations

    @property
    def all_pools(self):
        return self.pools.all()

    @property
    def number_of_pools(self):
        return self.pools.count()

    def calculate_and_pop_full_pools(self, pools):
        full_pools = [pool for pool in pools if pool.is_full]
        for pool in full_pools:
            pools.remove(pool)
        return full_pools

    def calculate_potential_members(self, pools):
        potential_members = {}
        for pool in pools:
            potential_users = 0
            for group in pool.permission_groups.all():
                potential_users += group.users.count()
            potential_members[pool] = potential_users
        return potential_members

    def find_most_exclusive_pools(self, potential_members):
        lowest = potential_members[min(potential_members, key=potential_members.get)]
        equal_pools = []
        for pool, members in potential_members.items():
            if members == lowest:
                equal_pools.append(pool)
        return equal_pools

    def select_highest_capacity(self, pools):
        capacities = [pool.capacity for pool in pools]
        return pools[capacities.index(min(capacities))]



class Pool(BasisModel):
    """
    Pool which keeps track of users able to register from different grades/groups.
    """

    name = models.CharField(max_length=100)
    capacity = models.PositiveSmallIntegerField(default=0)
    event = models.ForeignKey(Event, related_name='pools')
    activation_date = models.DateTimeField()
    permission_groups = models.ManyToManyField(AbakusGroup)

    @property
    def number_of_registrations(self):
        return self.registrations.count()

    @property
    def is_full(self):
        return self.number_of_registrations >= self.capacity

    def __str__(self):
        return self.name


class WaitingList(BasisModel):
    """
    List of registrations that keeps track of users who registered after the event was full.
    """
    event = models.OneToOneField(Event, related_name="waiting_list")

    @property
    def number_of_registrations(self):
        return self.registrations.count()

    def add(self, user, pools):
        """
        Adds a user to the waiting list, along with what pools the user is waiting for.

        :param pools: Pools that the user is allowed to join, saved for bumping (used in pop).
        :return: A registration for this waiting list, with `pool=null` and `waiting_pools=pools`
        """
        reg = self.registrations.create(event=self.event,
                                        user=user,
                                        waiting_list=self)
        for pool in pools:
            reg.waiting_pool.add(pool)
        return reg

    def pop(self, from_pool=None):
        """
        Pops the first user in the waiting list that can join `from_pool`.
        If `from_pool=None`, pops the first user in the waiting list overall.

        :param from_pool: The pool we are bumping to. If post-merge, there is no pool.
        :return: The registration that is first in line for said pool.
        """
        if from_pool:
            top = self.registrations.filter(waiting_pool__id=from_pool.id).first()
        else:
            top = self.registrations.first()
        top.waiting_list = None
        top.save()
        return top


class Registration(BasisModel):
    """
    A registration for an event. Can be connected to either a pool or a waiting list.
    """
    user = models.ForeignKey(User, related_name='registrations')
    event = models.ForeignKey(Event, related_name='registrations')
    pool = models.ForeignKey(Pool, null=True, related_name='registrations')
    waiting_list = models.ForeignKey(WaitingList, null=True, related_name='registrations')
    waiting_pool = models.ManyToManyField(Pool, null=True, related_name='waiting_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    unregistration_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return str({"user": self.user, "pool": self.pool})
