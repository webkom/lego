from django.db import models

from lego.apps.companies.models import Company, CompanyContact
from lego.apps.content.models import Content
from lego.utils.models import BasisModel


class Workplace(BasisModel):
    town = models.CharField(max_length=100)


class Joblisting(Content, BasisModel):
    YEAR_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )

    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    SUMMER_JOB = 'summer_job'
    OTHER = 'other'

    JOB_TYPE_CHOICES = (
        (FULL_TIME, FULL_TIME),
        (PART_TIME, PART_TIME),
        (SUMMER_JOB, SUMMER_JOB),
        (OTHER, OTHER),
    )

    company = models.ForeignKey(Company, related_name='joblistings')
    responsible = models.ForeignKey(CompanyContact, related_name='joblistings', null=True)
    deadline = models.DateTimeField(null=True)
    visible_from = models.DateTimeField(auto_now_add=True)
    visible_to = models.DateTimeField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    workplaces = models.ManyToManyField(Workplace)
    from_year = models.PositiveIntegerField(choices=YEAR_CHOICES, default='1')
    to_year = models.PositiveIntegerField(choices=YEAR_CHOICES, default='5')
    application_url = models.URLField(null=True, blank=True)
