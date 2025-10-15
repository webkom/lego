from django.db import models
from django.db.models import URLField

from lego.apps.companies.models import Company, CompanyContact
from lego.apps.content.models import Content
from lego.apps.joblistings.constants import JOB_TYPE_CHOICES, YEAR_CHOICES
from lego.apps.joblistings.permissions import JoblistingPermissionHandler
from lego.utils.models import BasisModel
from lego.utils.youtube_validator import youtube_validator


class Workplace(BasisModel):
    town = models.CharField(max_length=100)


class Joblisting(Content, BasisModel):
    company = models.ForeignKey(
        Company, related_name="joblistings", on_delete=models.CASCADE
    )
    responsible = models.ForeignKey(
        CompanyContact, related_name="joblistings", null=True, on_delete=models.SET_NULL
    )
    contact_mail = models.EmailField(blank=True)
    deadline = models.DateTimeField(null=True)
    visible_from = models.DateTimeField()
    visible_to = models.DateTimeField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    workplaces = models.ManyToManyField(Workplace)
    from_year = models.PositiveIntegerField(choices=YEAR_CHOICES, default="1")
    to_year = models.PositiveIntegerField(choices=YEAR_CHOICES, default="5")
    application_url = models.URLField(null=True, blank=True)
    youtube_url = URLField(default="", validators=[youtube_validator], blank=True)
    rolling_recruitment = models.BooleanField(default=False, null=False, blank=False)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        permission_handler = JoblistingPermissionHandler()
