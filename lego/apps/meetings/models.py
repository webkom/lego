from django.conf import settings
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import models

from lego.apps.content.models import Content
from lego.apps.meetings import constants
from lego.apps.meetings.permissions import (MeetingInvitationPermissionHandler,
                                            MeetingPermissionHandler)
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Meeting(Content, BasisModel):

    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    report = models.TextField(blank=True)
    report_author = models.ForeignKey(User, blank=True, null=True, related_name='meetings_reports')
    _invited_users = models.ManyToManyField(User, through='MeetingInvitation',
                                            related_name='meeting_invitation',
                                            through_fields=('meeting', 'user'))

    class Meta:
        permission_handler = MeetingPermissionHandler()

    @property
    def invited_users(self):
        """
        As _invited_users include invitations deleted by Meeting.uninvite,
        we need to use this property method to not show them.
        For some reason, limit_choices_to does not work with ManyToManyField
        when specifying a custom through table.
        """
        return self._invited_users.filter(invitations__deleted=False)

    def get_absolute_url(self):
        return f'{settings.FRONTEND_URL}/meetings/{self.id}/'

    @property
    def participants(self):
        return self.invited_users.filter(invitations__status=constants.ATTENDING)

    def invite_user(self, user, created_by=None):
        invitation, created = self.invitations.update_or_create(
            user=user,
            meeting=self,
            defaults={
                'created_by': created_by
            }
        )

        return invitation, created

    def invite_group(self, group, created_by=None):
        for user in group.users.all():
            self.invite_user(user, created_by)

    def uninvite_user(self, user):
        invitation = self.invitations.get(user=user)
        invitation.delete(force=True)

    def restricted_lookup(self):
        """
        Restricted mail
        """
        return self.invited_users, []

    def announcement_lookup(self):
        return self.invited_users


class MeetingInvitation(BasisModel):

    meeting = models.ForeignKey(Meeting, related_name='invitations')
    user = models.ForeignKey(User, related_name='invitations')
    status = models.CharField(
        max_length=50, choices=constants.INVITATION_STATUS_TYPES, default=constants.NO_ANSWER
    )

    class Meta:
        unique_together = ('meeting', 'user')
        permission_handler = MeetingInvitationPermissionHandler()

    def generate_invitation_token(self):
        data = signing.dumps({
            'user_id': self.user.id,
            'meeting_id': self.meeting.id
        })

        token = TimestampSigner().sign(data)
        return token

    @staticmethod
    def validate_token(token):
        """
        Validate token.

        returns MeetingInvitation or None
        """

        try:
            # Valid in 7 days
            valid_in = 60 * 60 * 24 * 7
            data = signing.loads(TimestampSigner().unsign(token, max_age=valid_in))

            return MeetingInvitation.objects.filter(
                user=int(data['user_id']),
                meeting=int(data['meeting_id'])
            )[0]
        except (BadSignature, SignatureExpired):
            return None

    def accept(self):
        self.status = constants.ATTENDING
        self.save()

    def reject(self):
        self.status = constants.NOT_ATTENDING
        self.save()
