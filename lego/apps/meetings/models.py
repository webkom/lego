from django.db import models

from lego.apps.content.models import SlugContent
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Meeting(SlugContent, BasisModel):

    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    report = models.TextField(blank=True)
    report_author = models.ForeignKey(User, blank=True, null=True, related_name='meetings_reports')
    _invited_users = models.ManyToManyField(User, through='MeetingInvitation',
                                            related_name='meeting_invitation',
                                            through_fields=('meeting', 'user'))

    @property
    def invited_users(self):
        """
        As _invited_users include invitations deleted by Meeting.uninvite,
        we need to use this property method to not show them.
        For some reason, limit_choices_to does not work with ManyToManyField
        when specifying a custom through table.
        """
        return self._invited_users.filter(invitation__deleted=False)

    @property
    def participants(self):
        return self.invited_users.filter(invitation__status=MeetingInvitation.ATTENDING)

    def invite(self, user):
        return self.invitation.update_or_create(user=user,
                                                meeting=self)

    def uninvite(self, user):
        invitation = self.invitation.get(user=user)
        invitation.delete()

    def can_edit(self, user):
        return self.created_by == user or self.invited_users.filter(id=user.id).exists()


class MeetingInvitation(BasisModel):

    NO_ANSWER = 0
    ATTENDING = 1
    NOT_ATTENDING = 2

    INVITATION_STATUS_TYPES = (
        (NO_ANSWER, 'No answer'),
        (ATTENDING, 'Attending'),
        (NOT_ATTENDING, 'Not attending')
    )

    meeting = models.ForeignKey(Meeting, related_name='invitation')
    user = models.ForeignKey(User, related_name='invitation')
    status = models.SmallIntegerField(choices=INVITATION_STATUS_TYPES,
                                      default=NO_ANSWER)

    def accept(self):
        self.status = self.ATTENDING
        self.save()

    def reject(self):
        self.status = self.NOT_ATTENDING
        self.save()

    class Meta:
        unique_together = ('meeting', 'user')
