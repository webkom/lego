from basis.models import BasisModel
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from lego.app.content.models import Content
from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import AbakusGroup, User

from .exceptions import NoAvailablePools


class Event(Content, BasisModel, ObjectPermissionsModel):

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
        return self.registrations.create(event=self, user=user, pool=pool)

    def register(self, user):
        # Create a list of all pools the user can join, based solely on permissions
        possible_pools = [_pool
                          for _pool in self.all_pools
                          if self.can_register(user, _pool)]
        # If there is only one possible pool, and the event only has one pool, we
        # can skip a lot of the logic used to pick the correct pool.
        if len(possible_pools) == 1 and self.number_of_pools == 1:
            if possible_pools[0].is_full:
                return self.waiting_list.add(user=user, pools=possible_pools)
            else:
                return self.registrations.create(event=self, pool=possible_pools[0], user=user)

        if not possible_pools:
            raise NoAvailablePools()

        # If the event isn't merged we need to calculate which pools have room for the user.
        if not self.is_merged:

            # Removes pools that are full, and adds them to a list to be used in
            # the waiting list, so that we can remember what pools are available
            # for the user, in case of a bump
            full_pools = [_pool for _pool in possible_pools if _pool.is_full]
            for _pool in full_pools:
                possible_pools.remove(_pool)

            # Adds user to waiting list if no possible pools are left
            if not possible_pools:
                return self.waiting_list.add(user=user, pools=full_pools)

        # If the event is merged, but full. we don't need to check each pool if it is full,
        # we can just check the event it self. The user is added to the waiting list for all
        # pools, since the event is merged.

        elif self.is_full:
            return self.waiting_list.add(user=user, pools=possible_pools)
        # Notice that if the event is merged but not full the user can now join
        # any permitted pool, even one that is full. Full pools are no longer a concept after
        # merging.

        # We want the user to join the most 'exclusive' pool, i.e. the one with
        # the lowest amount of potential members.
        # Calculate the amount of members that could potentially
        # try and join each pool
        potential_capacities = [sum(group.users.count()
                                for group in _pool.permission_groups.all())
                                for _pool in possible_pools]

        # Find the lowest of these amounts
        lowest = min(potential_capacities)
        equal_pools = [index
                       for index in range(len(potential_capacities))
                       if potential_capacities[index] == lowest]

        # If only one pool has that amount, select it. If several
        # pools have this amount we choose the one with the lowest capacity.
        # Maybe this should check for the one with highest capacity instead?
        # I don't fucking know. If so, we need to change some of the tests.
        if len(equal_pools) == 1:
            chosen_pool = possible_pools[equal_pools[0]]
        else:
            capacities = [_pool.capacity
                          for _pool in possible_pools]
            chosen_pool = possible_pools[capacities.index(min(capacities))]

        return self.registrations.create(event=self, user=user, pool=chosen_pool)

    def unregister(self, user):
        registration = self.registrations.get(user=user)
        pool = registration.pool
        registration.pool = None
        registration.waiting_list = None
        registration.waiting_pool.clear()
        registration.unregistration_date = timezone.now()
        registration.save()
        if pool:
            self.notify_unregistration(pool)

    def notify_unregistration(self, pool):
        if self.number_of_registrations < self.capacity:
            if self.is_merged:
                self.bump()
            elif pool.waiting_registrations.count() > 0:
                self.bump(from_pool=pool)

    def bump(self, from_pool=None):
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
        capacity = 0
        for pool in self.all_pools:
            if self.is_activated(pool):
                capacity += pool.capacity
        return capacity

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


class Pool(BasisModel):
    """
    Pool which keeps track of users able to register from different grades.
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
    event = models.OneToOneField(Event, related_name="waiting_list")

    @property
    def number_of_registrations(self):
        return self.registrations.count()

    def add(self, user, pools):
        reg = self.registrations.create(event=self.event,
                                        user=user,
                                        waiting_list=self)
        for _pool in pools:
            reg.waiting_pool.add(_pool)
        return reg

    def pop(self, from_pool=None):
        if from_pool:
            top = self.registrations.filter(waiting_pool__id=from_pool.id).first()
        else:
            top = self.registrations.first()
        top.waiting_list = None
        top.save()
        return top


class Registration(BasisModel):
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
