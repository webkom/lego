from django.db import models

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Company(BasisModel, ObjectPermissionsModel):
    """
    These are the values returned when calling without specific route
    """
    defaut_semester = {
        "year": 2016,
        "semester": 0,
        "contacted_status": 6
    }
    name = models.CharField(max_length=100)
    student_contact = models.ForeignKey(User, related_name='companies')
    previous_contacts = models.ManyToManyField(User)
    admin_comment = models.CharField(max_length=100, default='', blank=True)
    job_offer_only = models.BooleanField(default=False)
    """
    These are the detail route-only fields
    """
    phone = models.CharField(max_length=100, default='', blank=True)

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

    year = models.PositiveSmallIntegerField(default=2016)
    semester = models.PositiveSmallIntegerField(choices=SEMESTERS, default=0)
    contacted_status = models.PositiveSmallIntegerField(choices=CONTACT_STATUSES, default=6)
    company = models.ForeignKey(Company, related_name='semester_statuses')
