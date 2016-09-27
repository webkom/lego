from basis.models import BasisModel
from django.db import models

from lego.apps.content.models import SlugContent
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import User


class Meeting(SlugContent, BasisModel, ObjectPermissionsModel):

    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    report = models.TextField(blank=True)
    report_author = models.ForeignKey(User, blank=True, null=True, related_name='meetings_reports')

    def invited_users(self):
        return self.invitations.values('user')

    def invite(self, user):
        return self.invitations.update_or_create(user=user,
                                                 meeting=self,
                                                 defaults={'status': MeetingInvitation.NO_ANSWER})


class Participant(BasisModel, ObjectPermissionsModel):
    meeting = models.ForeignKey(Meeting, related_name='participants')
    user = models.ForeignKey(User)


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
    user = models.ForeignKey(User, related_name='meeting_invitations')

    def accept(self):
        self.status = self.ATTENDING
        self.meeting.participants.update_or_create(meeting=self.meeting, user=self.user)
        self.save()

    def reject(self):
        self.status = self.NOT_ATTENDING
        self.save()
