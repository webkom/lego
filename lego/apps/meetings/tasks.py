from datetime import timedelta

from django.utils import timezone

from structlog import get_logger

from lego import celery_app
from lego.apps.meetings import constants
from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.meetings.notifications import MeetingInvitationReminderNotification
from lego.apps.users.models import User
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def notify_user_of_unanswered_meeting_invitation(self, logger_context=None):
    self.setup_logger(logger_context)

    meetings: list[Meeting] = Meeting.objects.filter(
        start_time__gt=timezone.now(),
        # Only send reminder when it's less than or equal to 7 days till start
        start_time__lte=timezone.now() + timedelta(days=7),
        # Only send reminder 2 days after creation
        created_at__lte=timezone.now() - timedelta(days=2),
    )

    for meeting in meetings:
        # Only send reminder if it's 7, 5, 3 or 1 day till start
        if (meeting.start_time.day - timezone.now().day) % 2 == 0:
            continue

        users: list[User] = meeting.invited_users.filter(
            invitations__status=constants.NO_ANSWER
        )
        for user in users:
            log.info(
                "user_notified_of_unanswered_meeting_invitation",
                meeting_id=meeting.id,
                user_id=user.id,
            )
            meeting_invitation = MeetingInvitation.objects.filter(
                meeting=meeting, user=user
            ).first()
            notification = MeetingInvitationReminderNotification(
                user, meeting_invitation=meeting_invitation
            )
            notification.notify()
