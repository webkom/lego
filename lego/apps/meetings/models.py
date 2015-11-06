from basis.models import BasisModel
from django.db import models

from lego.apps.content.models import Content
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import User


class Meeting(Content, BasisModel, ObjectPermissionsModel):

    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)

    report = models.TextField(null=True)
    report_author = models.ForeignKey(User, null=True, related_name='meetings_reports')

    # def invite(self, user):
    #     self.invitations.update_or_create()


class MeetingInvitation(BasisModel, ObjectPermissionsModel):

    NO_ANSWER = 0
    ATTENDING = 1
    NOT_ATTENDING = 2

    INVITATION_STATUS_TYPES = (
        (NO_ANSWER, 'No answer'),
        (ATTENDING, 'Attending'),
        (NOT_ATTENDING, 'Not attending')
    )

    meeting = models.ForeignKey(Meeting, related_name='invitations')
    status = models.SmallIntegerField(choices=INVITATION_STATUS_TYPES)
