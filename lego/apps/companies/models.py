from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from lego.apps.comments.models import Comment
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Company(BasisModel, ObjectPermissionsModel):

    defaut_semester = {
        "year": 2016,
        "semester": 0,
        "contacted_status": 6
    }

    """ These are the values returned when calling without specific route """
    name = models.CharField(max_length=100)
    student_contact = models.ForeignKey(User, related_name='companies')
    admin_comment = models.CharField(max_length=100, default='', blank=True)
    active = models.BooleanField(default=True)
    job_offer_only = models.BooleanField(default=False)
    bedex = models.BooleanField(default=False)

    """ These are the detail route-only fields """
    description = models.CharField(max_length=500, default='')
    phone = models.CharField(max_length=100, default='', blank=True)
    website = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=100, default='')
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
    SEMESTERS = (
        (0, 'Vår'),
        (1, 'Høst')
    )

    CONTACT_STATUSES = (
        (0, 'Bedpres'),
        (1, 'Bedpres & Kurs'),
        (2, 'Kurs'),
        (3, 'Interessert, ikke tilbudt'),
        (4, 'Ikke interessert'),
        (5, 'Kontaktet'),
        (6, 'Ikke kontaktet')
    )

    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField(choices=SEMESTERS, default=0)
    contacted_status = models.PositiveSmallIntegerField(choices=CONTACT_STATUSES, default=6)
    contract = models.CharField(max_length=500, default='')
    company = models.ForeignKey(Company, related_name='semester_statuses')

    class Meta:
        unique_together = ('year', 'semester', 'company')


class CompanyContact(BasisModel):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default='')
    mail = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=100, default='')
    company = models.ForeignKey(Company, related_name='company_contacts')
