from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from lego.apps.comments.models import Comment
from lego.apps.users.models import User
from lego.utils.models import BasisModel

from .constants import CONTACT_STATUSES, SEMESTERS


class Company(BasisModel):

    """ These are the values returned when calling without specific route """
    name = models.CharField(max_length=100)
    student_contact = models.ForeignKey(User, related_name='companies', blank=True, null=True)
    admin_comment = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)

    """ These are the detail route only fields """
    description = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    company_type = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    payment_mail = models.EmailField(max_length=100, blank=True)
    previous_contacts = models.ManyToManyField(User)
    comments = GenericRelation(Comment)

    @property
    def comment_target(self):
        return '{0}.{1}-{2}'.format(self._meta.app_label, self._meta.model_name, self.pk)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class SemesterStatus(BasisModel):
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField(choices=SEMESTERS, default=0)
    contacted_status = models.PositiveSmallIntegerField(choices=CONTACT_STATUSES, default=6)
    contract = models.CharField(max_length=500, blank=True)
    company = models.ForeignKey(Company, related_name='semester_statuses')

    class Meta:
        unique_together = ('year', 'semester', 'company')


class CompanyContact(BasisModel):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    mail = models.EmailField(max_length=100, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey(Company, related_name='company_contacts')
