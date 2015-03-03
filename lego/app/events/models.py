from basis.models import BasisModel
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from lego.app.content.models import Content
from lego.users.models import User

from .exceptions import EventFullException


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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)

    def slug(self):
        return slugify(self.title)

    def add_pool(self, name, size, activation_date):
        return self.pools.create(name=name, size=size, activation_date=activation_date)

    def can_register(self, user=None, pool=None):
        """
        Checks whether an user is able to register for an event.
        """

        if pool is None:
            return False

        if not self.is_activated(pool):
            return False

        if self.is_full or pool.size <= pool.number_of_registrations and not self.is_merged:
            raise EventFullException()

        if self.user_in_pool(user, pool):
            if self.number_of_pools == 1 or self.is_merged:
                return True
            elif self.number_of_pools > 1:
                return pool.size > pool.number_of_registrations

    def register(self, user=None, pool=None):
        if self.can_register(user, pool) and pool is not None:
            return pool.register(user)

    def is_activated(self, pool):
        return pool.activation_date <= timezone.now()

    @property
    def is_merged(self):
        if self.number_of_pools > 1:
            return timezone.now() >= self.merge_time

    @property
    def is_full(self):
        return self.total_capacity_count <= self.total_registrations_count

    @property
    def total_capacity_count(self):
        """
        Calculates total capacity of participants with or without multiple pools.
        """

        capacity = 0
        if self.number_of_pools > 0:
            for pool in self.all_pools:
                if self.is_activated(pool):
                    capacity += pool.size
        return capacity

    @property
    def total_registrations_count(self):
        """
        Calculates total registrations with or without multiple pools.
        """

        registrations = 0
        if self.number_of_pools > 0:
            for pool in self.all_pools:
                registrations += pool.number_of_registrations
        return registrations

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
    size = models.PositiveSmallIntegerField(default=0)
    event = models.ForeignKey(Event, related_name='pools')
    activation_date = models.DateTimeField()

    def __str__(self):
        return self.name

    @property
    def number_of_registrations(self):
        return self.registrations.count()

    def register(self, user):
        return self.registrations.create(pool=self, user=user)


class Registration(BasisModel):

    user = models.ForeignKey(User, null=True, related_name='registrations')
    pool = models.ForeignKey(Pool, related_name='registrations')

    class Meta:
        unique_together = ('user', 'pool')

    def __str__(self):
        return self.user, self.pool
