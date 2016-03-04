from basis.models import BasisModel
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from lego.app.content.models import Content
from lego.permissions.models import ObjectPermissionsModel


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

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)

    def slug(self):
        return slugify(self.title)
