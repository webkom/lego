from django.db import models

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from lego.app.content.models import Content


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

    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPES, verbose_name=_("Event ype"))
    location = models.CharField(max_length=100, verbose_name=_("Location"))

    start_time = models.DateTimeField(verbose_name=_("Start time"))
    end_time = models.DateTimeField(verbose_name=_("End time"))

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(self.save(*args, **kwargs))

    def slug(self):
        return slugify(self.name)
