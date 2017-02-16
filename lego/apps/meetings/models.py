from django.core import signing, urlresolvers
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import models

from lego.apps.content.models import Content
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

    @property
    def invited_users(self):
        """
        As _invited_users include invitations deleted by Meeting.uninvite,
        we need to use this property method to not show them.
        For some reason, limit_choices_to does not work with ManyToManyField
        when specifying a custom through table.
        """
        return self._invited_users.filter(invitations__deleted=False)

    @property
    def participants(self):
        return self.invited_users.filter(invitations__status=MeetingInvitation.ATTENDING)

    def invite_user(self, user):
        invitation = self.invitations.update_or_create(user=user,
                                                       meeting=self)

        # TODO think about "double" invite
        accept_url = urlresolvers.reverse('api:v1:meeting-token-accept')
        reject_url = urlresolvers.reverse('api:v1:meeting-token-reject')

        token = invitation[0].generate_invitation_token()
        send_mail(
            subject=f'Invitasjon til møte: {self.title}',
            message=(f'Hei {user.get_short_name()},\n\n'
                     f'Du ble invitert til møte:\n\n'
                     f'Dato: {self.start_time}\n\n'
                     f'{self.report}\n\n'
                     f'Delta på møte: {accept_url}?token={token}\n'
                     f'Ikke delta på møte: {reject_url}?token={token}'),
            recipient_list=[user.email],
            from_email='webkom@abakus.no'
        )

        return invitation

    def invite_group(self, group):
        for user in group.users.all():
            self.invite_user(user)

    def uninvite_user(self, user):
        invitation = self.invitations.get(user=user)
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

    meeting = models.ForeignKey(Meeting, related_name='invitations')
    user = models.ForeignKey(User, related_name='invitations')
    status = models.SmallIntegerField(choices=INVITATION_STATUS_TYPES,
                                      default=NO_ANSWER)

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
        self.status = self.ATTENDING
        self.save()

    def reject(self):
        self.status = self.NOT_ATTENDING
        self.save()

    class Meta:
        unique_together = ('meeting', 'user')
