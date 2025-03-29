from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models

from lego.apps.comments.models import Comment
from lego.apps.companies.permissions import (
    CompanyContactPermissionHandler,
    CompanyInterestPermissionHandler,
    CompanyPermissionHandler,
    NestedCompanyPermissionHandler,
    SemesterPermissionHandler,
)
from lego.apps.files.models import FileField
from lego.apps.users.models import User
from lego.utils.models import BasisModel, PersistentModel, TimeStampModel

from .constants import (
    AUTUMN,
    COLLABORATIONS,
    COMPANY_COURSE_THEMES,
    COMPANY_EVENTS,
    COMPANY_TYPES,
    OTHER_OFFERS,
    SEMESTER,
    SEMESTER_STATUSES,
    SPRING,
    TRANSLATED_COLLABORATIONS,
    TRANSLATED_EVENTS,
    TRANSLATED_OTHER_OFFERS,
)


class Semester(BasisModel):
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=64, choices=SEMESTER)
    active_interest_form = models.BooleanField(default=False)

    class Meta:
        unique_together = ("year", "semester")
        permission_handler = SemesterPermissionHandler()


class Company(BasisModel):
    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    company_type = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    payment_mail = models.EmailField(max_length=100, blank=True)
    comments = GenericRelation(Comment)

    logo = FileField(related_name="company_logos")

    class Meta:
        permission_handler = CompanyPermissionHandler()
        ordering = ["name"]

    @property
    def content_target(self) -> str:
        return "{0}.{1}-{2}".format(
            self._meta.app_label, self._meta.model_name, self.pk
        )

    def __str__(self) -> str:
        return self.name


class StudentCompanyContact(BasisModel):
    company = models.ForeignKey(
        Company, related_name="student_contacts", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="contact_for_companies", on_delete=models.CASCADE
    )
    semester = models.ForeignKey(
        Semester, related_name="student_contacts", on_delete=models.CASCADE
    )


class CompanyFile(models.Model):
    company = models.ForeignKey(Company, related_name="files", on_delete=models.CASCADE)
    file = FileField()


class SemesterStatus(TimeStampModel):
    company = models.ForeignKey(
        Company, related_name="semester_statuses", on_delete=models.CASCADE
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    contacted_status = ArrayField(
        models.CharField(choices=SEMESTER_STATUSES, max_length=64),
        null=True,
        blank=True,
    )
    contract = FileField(related_name="semester_status_contracts")
    statistics = FileField(related_name="semester_status_statistics")
    evaluation = FileField(related_name="semester_status_evaluations")

    class Meta:
        unique_together = ("semester", "company")
        permission_handler = NestedCompanyPermissionHandler()


class CompanyContact(BasisModel):
    company = models.ForeignKey(
        Company, related_name="company_contacts", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    mail = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=100, blank=True)
    public = models.BooleanField(default=False)

    class Meta:
        permission_handler = CompanyContactPermissionHandler()


class CompanyInterest(PersistentModel, TimeStampModel):
    """
    Either company_name OR company should be null. We prefer to use a Foreign key to
    an existing company when making a Company Interest, because that lets us
    do things like update the BDB status for that company to "interested".
    It still needs to be possible to register interest without being in the BDB,
    however, in which case company is Null and the string company_name is used instead.
    """

    company = models.ForeignKey(
        Company,
        related_name="company_interests",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    company_name = models.CharField(max_length=255, blank=True)

    contact_person = models.CharField(max_length=255)
    mail = models.EmailField()
    phone = models.CharField(max_length=100, blank=True)
    semesters = models.ManyToManyField(Semester, blank=True)
    events = ArrayField(
        models.CharField(max_length=64, choices=COMPANY_EVENTS), null=True, blank=True
    )
    other_offers = ArrayField(
        models.CharField(max_length=64, choices=OTHER_OFFERS), null=True, blank=True
    )
    collaborations = ArrayField(
        models.CharField(max_length=64, choices=COLLABORATIONS), null=True, blank=True
    )
    company_type = models.CharField(
        max_length=64, null=True, choices=COMPANY_TYPES.choices, blank=True
    )
    company_course_themes = ArrayField(
        models.CharField(max_length=64, choices=COMPANY_COURSE_THEMES.choices),
        null=True,
        blank=True,
    )
    office_in_trondheim = models.BooleanField(default=False, blank=True)
    wants_thursday_event = models.BooleanField(default=False, blank=True)

    target_grades = ArrayField(models.PositiveIntegerField(), null=True, blank=True)
    participant_range_start = models.IntegerField(null=True, blank=True)
    participant_range_end = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    course_comment = models.TextField(blank=True)
    breakfast_talk_comment = models.TextField(blank=True)
    other_event_comment = models.TextField(blank=True)
    startup_comment = models.TextField(blank=True)
    company_to_company_comment = models.TextField(blank=True)
    lunch_presentation_comment = models.TextField(blank=True)
    company_presentation_comment = models.TextField(blank=True)
    bedex_comment = models.TextField(blank=True)

    class Meta:
        permission_handler = CompanyInterestPermissionHandler()

    def generate_mail_context(self):
        semesters = []
        for semester in self.semesters.all():
            if semester.semester == SPRING:
                semesters.append(f"Vår {semester.year}")
            elif semester.semester == AUTUMN:
                semesters.append(f"Høst {semester.year}")

        events = []
        for event in self.events:
            events.append(TRANSLATED_EVENTS[event])

        others = []
        for offer in self.other_offers:
            others.append(TRANSLATED_OTHER_OFFERS[offer])

        collaborations = []
        for collab in self.collaborations:
            collaborations.append(f"Samarbeid med {TRANSLATED_COLLABORATIONS[collab]}")

        grades = [f"{g}.kl" for g in self.target_grades]

        readme = "readme" in self.other_offers

        return {
            "company_name": self.company_name,
            "contact_person": self.contact_person,
            "mail": self.mail,
            "semesters": ", ".join(semesters),
            "events": ", ".join(events),
            "others": ", ".join(others),
            "collaborations": ", ".join(collaborations),
            "target_grades": ", ".join(grades),
            "participant_range": f"{self.participant_range_start} - {self.participant_range_end}",
            "comment": self.comment,
            "course_comment": self.course_comment,
            "breakfast_talk_comment": self.breakfast_talk_comment,
            "other_event_comment": self.other_event_comment,
            "startup_comment": self.startup_comment,
            "company_to_company_comment": self.company_to_company_comment,
            "lunch_presentation_comment": self.lunch_presentation_comment,
            "company_presentation_comment": self.company_presentation_comment,
            "bedex_comment": self.bedex_comment,
            "readme": readme,
        }
