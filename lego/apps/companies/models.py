from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models

from lego.apps.comments.models import Comment
from lego.apps.users.models import User
from lego.utils.models import BasisModel, TimeStampModel

from .constants import COMPANY_EVENTS, SEMESTER, SEMESTER_STATUSES


class Semester(BasisModel):
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=64, choices=SEMESTER)

    class Meta:
        unique_together = ('year', 'semester')


class Company(BasisModel):
    name = models.CharField(max_length=100)
    student_contact = models.ForeignKey(User, related_name='companies', blank=True, null=True)
    previous_contacts = models.ManyToManyField(User)

    description = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    company_type = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    payment_mail = models.EmailField(max_length=100, blank=True)
    comments = GenericRelation(Comment)

    @property
    def comment_target(self):
        return '{0}.{1}-{2}'.format(self._meta.app_label, self._meta.model_name, self.pk)

    def __str__(self):
        return self.name


class SemesterStatus(TimeStampModel):
    company = models.ForeignKey(Company, related_name='semester_statuses')
    semester = models.ForeignKey(Semester)
    contacted_status = ArrayField(models.CharField(choices=SEMESTER_STATUSES, max_length=64))

    class Meta:
        unique_together = ('semester', 'company')


class CompanyContact(BasisModel):
    company = models.ForeignKey(Company, related_name='company_contacts')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    mail = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=100, blank=True)


class CompanyInterest(BasisModel):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    mail = models.EmailField()
    semesters = models.ManyToManyField(Semester, blank=True)
    events = ArrayField(models.CharField(max_length=64, choices=COMPANY_EVENTS))
    read_me = models.BooleanField(default=False)
    collaboration = models.BooleanField(default=False)
    itdagene = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
