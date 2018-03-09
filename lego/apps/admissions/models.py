from django.db import models
from django.utils import timezone

from lego.apps.content.models import SlugModel
from lego.apps.users.models import AbakusGroup, User
from lego.utils.models import BasisModel, TimeStampModel


class Admission(TimeStampModel):
    title = models.CharField(max_length=255)
    open_from = models.DateTimeField()
    public_deadline = models.DateTimeField()
    application_deadline = models.DateTimeField()

    def __str__(self):
        return self.title

    @property
    def is_closed(self):
        return timezone.now() > self.application_deadline

    @property
    def is_appliable(self):
        return self.public_deadline > timezone.now() > self.open_from


class Committee(BasisModel):
    group = models.OneToOneField(AbakusGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    response_label = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Application(models.Model):
    admission = models.ForeignKey(Admission, related_name='applications', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)

    time_sent = models.DateTimeField(editable=False, null=True)

    #def delete(self, using=None, force=True): # If we want BasisModel (or maybe we want timestamp? Do we need time sent?)
    #    super().delete(using, force)

    class Meta:
        unique_together = ('admission', 'user')

    @property
    def is_editable(self):
        return not self.admission.is_closed

    @property
    def is_sendable(self):
        return self.is_editable and self.committee_applications.exists()

    @property
    def applied_within_deadline(self):
        return self.time_sent < self.admission.public_deadline

    @property
    def sent(self):
        return bool(self.time_sent)

    def has_committee_application(self, committee):
        return self.committee_applications.filter(committee=committee).exists()

class CommitteeApplication(models.Model):
    application = models.ForeignKey(Application, related_name='committee_applications', on_delete=models.CASCADE)
    committee = models.ForeignKey(Committee, related_name='applications', on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField(null=True)
    text = models.TextField(blank=True)