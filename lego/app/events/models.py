# -*- coding: utf8 -*-
from basis.models import BasisModel
from django.db import models

from lego.users.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Event(BasisModel):

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

    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Name"))
    type = models.PositiveSmallIntegerField(choices=EVENT_TYPES, verbose_name=_("Type"))
    creator = models.ForeignKey(User, editable=False, null=True, blank=True, verbose_name=_("Creator"))
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Location"))

    start_date = models.DateTimeField(verbose_name=_("Start date"))
    end_date = models.DateTimeField(verbose_name=_("End date"))

    class Meta:
        ordering = ["start_date"]
        verbose_name = _("Event")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(self.save(*args, **kwargs))

    def slug(self):
        return slugify(self.name)

    @property
    def capacity_count(self):
        """
        Calculates total capacity of participants with or without multiple pools.
        """

        capacity = 0
        if self.pools.count() > 0:
            for pool in self.pools.all():
                capacity += pool.size
        return capacity

    def add_pool(self, name, size):
        return self.pools.create(name=name, size=size)



class Pool(BasisModel):
    """
    Pool which keeps track of maximum number of users able to register from different grades.
    """

    name = models.CharField(max_length=100, verbose_name=_("Pool name"))
    size = models.PositiveSmallIntegerField(default=0, verbose_name=_("Pool size"))
    event = models.ForeignKey(Event, verbose_name=_("Event"), related_name="pools")

    def __str__(self):
        return self.name
