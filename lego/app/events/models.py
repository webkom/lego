from basis.models import BasisModel
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from lego.app.content.models import Content
from lego.users.models import AbakusGroup, User


class Event(Content):

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

    def register(self, user, pool=None):
        use_waiting_list = False
        if not pool:
            possible_pools = []
            for _pool in self.all_pools:
                if self.can_register(user, _pool):
                    possible_pools.append(_pool)

            if len(possible_pools) == 0:
                return False

            full_pools = []
            for _pool in possible_pools:
                if _pool.is_full():
                    full_pools.append(possible_pools.pop(possible_pools.index(_pool)))

            if len(possible_pools) == 0:
                return self.waiting_list.add(user=user, pool=full_pools)
            else:
                potential_capacities = []
                for _pool in possible_pools:
                    _potential = 0
                    for group in _pool.permission_groups.all():
                        _potential += group.users.count()
                    potential_capacities.append(_potential)
                lowest = min(potential_capacities)
                equal_pools = []
                for index in range(len(potential_capacities)):
                    if potential_capacities[index] == lowest:
                        equal_pools.append(index)
                if len(equal_pools) == 1:
                    chosen_pool = possible_pools[equal_pools[0]]
                else:
                    capacities = []
                    for _pool in possible_pools:
                        capacities.append(_pool.capacity)
                    chosen_pool = possible_pools[capacities.index(min(capacities))]
                return self.registrations.create(event=self, pool=chosen_pool, user=user)

        if not self.can_register(user, pool):
            return False

        if self.is_full or (pool.is_full() and not self.is_merged):
            use_waiting_list = True

        if use_waiting_list:
            return self.waiting_list.add(user=user, pool=[pool])
        else:
            return self.registrations.create(event=self, pool=pool, user=user)

    def unregister(self, user):
        registration = self.registrations.get(user=user)
        pool = registration.pool
        registration.delete()
        self.notify_unregistration(pool_unregistered_from=pool)

    def notify_unregistration(self, pool_unregistered_from):
        if (self.number_of_registrations < self.capacity and
                pool_unregistered_from is not None):
            if self.is_merged:
                self.bump()
            elif pool_unregistered_from.waiting_registrations.count() > 0:
                self.bump(from_pool=pool_unregistered_from)

    def bump(self, from_pool=None):
        if self.waiting_list.number_of_registrations > 0:
            top = self.waiting_list.pop(from_pool=from_pool)
            if from_pool:
                pool = top.waiting_pool.filter(id=from_pool.id)
                top.pool = pool[0]
            else:
                top.pool = top.waiting_pool.first()
            top.waiting_pool.clear()
            top.save()

    def is_activated(self, pool):
        return pool.activation_date <= timezone.now()

    @property
    def is_merged(self):
        if self.number_of_pools > 1:
            return timezone.now() >= self.merge_time

    @property
    def is_full(self):
        return self.capacity <= self.number_of_registrations

    def is_registered(self, user):
        return self.registrations.filter(user=user).exists()

    @property
    def capacity(self):
        """
        Calculates total capacity of participants with or without multiple pools.
        """
        capacity = 0
        for pool in self.all_pools:
            if self.is_activated(pool):
                capacity += pool.capacity
        return capacity

    @property
    def number_of_registrations(self):
        """
        Calculates total registrations with or without multiple pools.
        """
        return self.registrations.filter(waiting_list=None, waiting_pool=None).count()

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

    def is_full(self):
        return self.number_of_registrations >= self.capacity

    def __str__(self):
        return self.name


class WaitingList(BasisModel):
    event = models.OneToOneField(Event, related_name="waiting_list")

    @property
    def number_of_registrations(self):
        return self.registrations.count()

    def add(self, user, pool):
        reg = self.registrations.create(event=self.event,
                                        user=user,
                                        waiting_list=self)
        for _pool in pool:
            reg.waiting_pool.add(_pool)
        return reg

    def pop(self, from_pool=None):
        if from_pool:
            top = self.registrations.filter(waiting_pool=from_pool).first()
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

    class Meta:
        unique_together = ('user', 'pool')

    def __str__(self):
        return str({"user": self.user, "pool": self.pool})
