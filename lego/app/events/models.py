from basis.models import BasisModel
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from lego.app.content.models import Content
from lego.users.models import User


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
        permissions = ('retrieve_event', 'Can retrieve event'), ('list_event', 'Can list event')
        ordering = ['start_time']

    def save(self, *args, **kwargs):
        super(BasisModel, self).save(*args, **kwargs)
        waiting_list = WaitingList(event=self)
        waiting_list.save()

    def __str__(self):
        return self.title

    def slug(self):
        return slugify(self.title)

    def add_pool(self, name, capacity, activation_date):
        return self.pools.create(name=name, capacity=capacity, activation_date=activation_date)

    def can_register(self, user=None, pool=None):
        if pool is None:
            return False

        if not self.is_activated(pool):
            return False

        return self.user_in_pool(user, pool)

    def register(self, user, pool):
        use_waiting_list = False

        if not self.can_register(user, pool):
            return

        if self.is_full or (pool.capacity <= pool.number_of_registrations and not self.is_merged):
            use_waiting_list = True

        if use_waiting_list:
            return self.registrations.create(event=self,
                                             waiting_pool=pool,
                                             user=user,
                                             waiting_list=self.waiting_list)

        return self.registrations.create(event=self,
                                         pool=pool,
                                         user=user)

    def unregister(self, user):
        try:
            registration = self.registrations.get(user=user)
        except Registration.DoesNotExist:
            return

        pool = registration.pool
        registration.delete()
        self.notify_unregistration(pool_unregistered_from=pool)

    def notify_unregistration(self, pool_unregistered_from):
        if (self.number_of_registrations < self.capacity and
                pool_unregistered_from is not None):

            if self.is_merged:
                self.bump()
            else:
                self.bump(pool_unregistered_from)

    def bump(self, pool=None):
        if self.waiting_list.number_of_registrations > 0:
            top = self.waiting_list.pop(from_pool=pool)
            top.pool = top.waiting_pool
            top.waiting_pool = None
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
        return self.registrations.filter(waiting_list=None).count()

    @property
    def number_of_waiting_registrations(self):
        return self.waiting_list.number_of_registrations

    @property
    def all_pools(self):
        return self.pools.all()

    @property
    def number_of_pools(self):
        return self.pools.count()

    def user_in_pool(self, user, pool):
        """
        Dummy user check as of now.
        """

        return True


class Pool(BasisModel):
    """
    Pool which keeps track of users able to register from different grades.
    """

    name = models.CharField(max_length=100)
    capacity = models.PositiveSmallIntegerField(default=0)
    event = models.ForeignKey(Event, related_name='pools')
    activation_date = models.DateTimeField()

    @property
    def number_of_registrations(self):
        return self.registrations.count()

    def register(self, user):
        return self.registrations.create(pool=self, user=user)

    def is_full(self):
        return self.number_of_registrations < self.capacity

    def __str__(self):
        return self.name


class WaitingList(BasisModel):
    event = models.OneToOneField(Event, related_name="waiting_list")

    @property
    def number_of_registrations(self):
        return self.registrations.count()

    def add(self, user, pool):
        return self.registrations.create(waiting_pool=pool, waiting_list=self, user=user)

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
    waiting_pool = models.ForeignKey(Pool, null=True, related_name='waiting_registration')
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pool')

    def __str__(self):
        return self.user, self.pool
