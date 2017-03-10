from smtplib import SMTPException

from django.conf import settings
from django.template import Context, loader
from structlog import get_logger

from lego import celery_app
from lego.apps import meetings
from lego.apps.users.models import User

log = get_logger()


@celery_app.task(bind=True, default_retry_delay=(60 * 5))
def async_notify_user_about_invitation(self, meeting_id, user_id):
    """Send email to the invited user."""
    meeting = meetings.models.Meeting.objects.get(pk=meeting_id)
    user = User.objects.get(pk=user_id)

    invitation = meetings.models.MeetingInvitation.objects.filter(
        user=user,
        meeting=meeting
    )[0]

    token = invitation.generate_invitation_token()
    message = loader.get_template("email/meeting_invitation.html")

    context = Context({
        "name": user.get_short_name(),
        "owner": meeting.created_by.get_short_name(),
        "title": meeting.title,
        "report": meeting.report,
        "report_author": (
            meeting.report_author.get_short_name() if meeting.report_author else 'Ikke valgt'
        ),
        "token": token,
        "meeting_id": meeting.id,
        "settings": settings
    })

    try:
        user.email_user(
            subject=f'Invitasjon til møte: {meeting.title}',
            message=message.render(context),
        )
    except SMTPException as e:
        log.error(
            'email_invitations_send_email_error',
            exception=e,
            meeting_id=meeting_id,
            user_id=user_id
        )
        raise self.retry(exc=e, max_retries=3)
