from datetime import datetime, time, timedelta

from django.utils import timezone

from structlog import get_logger

from lego import celery_app
from lego.apps.meetings import constants
from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.meetings.notifications import MeetingInvitationReminderNotification
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
        if (
            datetime.combine(meeting.start_time, time(0))
            - datetime.combine(timezone.now(), time(0))
        ).days not in [7, 5, 3, 1] or meeting.is_template:
            continue

        meeting_invitations: list[MeetingInvitation] = meeting.invitations.filter(
            status=constants.NO_ANSWER
        )
        for meeting_invitation in meeting_invitations:
            log.info(
                "user_notified_of_unanswered_meeting_invitation",
                meeting_id=meeting.id,
                user_id=meeting_invitation.user.id,
            )
            notification = MeetingInvitationReminderNotification(
                meeting_invitation.user, meeting_invitation=meeting_invitation
            )
            notification.notify()


@celery_app.task(base=AbakusTask, bind=True)
def generate_weekly_recurring_meetings(self, logger_context=None):
    """Creates new weekly meetings"""
    self.setup_logger(logger_context)
    today = timezone.now()

    recurring_meetings = Meeting.objects.filter(
        is_recurring=True, parent__isnull=True, is_template=True
    )

    for meeting in recurring_meetings:
        next_start_time = meeting.get_next_occurrence()

        if not next_start_time or next_start_time < today:
            continue

        latest_report_entry = meeting.report_changelogs.order_by("-created_at").first()
        latest_report = latest_report_entry.report if latest_report_entry else ""

        future_meetings = Meeting.objects.filter(
            start_time__gte=today,
            parent=meeting,
            created_by=meeting.created_by,
            is_recurring=False,
            is_template=False,
        )

        if future_meetings.exists():
            continue

        meeting_duration = (
            (meeting.end_time - meeting.start_time)
            if meeting.end_time
            else timedelta(hours=1)
        )
        next_end_time = next_start_time + meeting_duration
        week_number = timezone.localtime(next_start_time).isocalendar()[1]
        new_title = f"{meeting.title} [Uke {week_number}]"

        new_meeting = Meeting.objects.create(
            title=new_title,
            location=meeting.location,
            mazemap_poi=meeting.mazemap_poi,
            start_time=next_start_time,
            end_time=next_end_time,
            description=meeting.description,
            is_recurring=False,
            is_template=False,
            parent=meeting,
            report=latest_report,
            current_user=meeting.created_by,
        )

        for user in meeting.invited_users.all():
            new_meeting.invite_user(user, created_by=meeting.created_by)
