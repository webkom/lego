from django.db import models
from django.utils.translation import ugettext_lazy as _

from lego.apps.articles.models import Article
from lego.utils.models import BasisModel


class Joblisting(BasisModel):
    title = models.CharField(max_length=100)
    content = models.OneToOneField(Article)

    YEAR_CHOICES = (
        (u'1',u'1'),
        (u'2',u'2'),
        (u'3',u'3'),
        (u'4',u'4'),
        (u'5',u'5')
    )

    FULL_TIME = 0
    PART_TIME = 1
    SUMMER_JOB = 2
    OTHER = 3

    JOB_TYPE_CHOICES = (
        (FULL_TIME, _('Full time')),
        (PART_TIME, _('Part time')),
        (SUMMER_JOB, _('Summer job')),
        (OTHER, _('Other')),
    )

    deadline = models.DateTimeField()
    visible_from = models.DateTimeField()
    visible_to = models.DateTimeField()
    job_type = models.PositiveIntegerField(choices=JOB_TYPE_CHOICES)
    workplaces = models.CharField(max_length=100)
    from_year = models.CharField(max_length=10, choices=YEAR_CHOICES, default='1')
    to_year = models.CharField(max_length=10, choices=YEAR_CHOICES, default='5')
    application_url = models.URLField(null=True, blank=True)
    application_email = models.EmailField(null=True, blank=True)
