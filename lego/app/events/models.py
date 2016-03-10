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
                return self.registrations.create(event=self, pool=possible_pools[0], user=user)

        if not self.is_merged:

            full_pools = self.calculate_and_pop_full_pools(possible_pools)

            if not possible_pools:
                return self.waiting_list.add(user=user, pools=full_pools)

        elif self.is_full:
            return self.waiting_list.add(user=user, pools=possible_pools)

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
        aggregate = self.all_pools.filter(activation_date__lte=timezone.now())\
            .aggregate(Sum('capacity'))
        return aggregate['capacity__sum']

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
        for pool in potential_members:
            if potential_members[pool] == lowest:
                equal_pools.append(pool)
        return equal_pools

    def select_highest_capacity(self, pools):
        capacities = [pool.capacity for pool in pools]
        return pools[capacities.index(min(capacities))]


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
