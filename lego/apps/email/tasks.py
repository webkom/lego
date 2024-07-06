from datetime import timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from premailer import transform
from structlog import get_logger

from lego import celery_app
from lego.apps.events.constants import EVENT_TYPE_TRANSLATIONS
from lego.apps.events.models import Event
from lego.apps.joblistings.constants import JOB_TYPE_TRANSLATIONS
from lego.apps.joblistings.models import Joblisting
from lego.apps.notifications.constants import EMAIL, WEEKLY_MAIL
from lego.apps.notifications.models import NotificationSetting
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.restricted.message_processor import MessageProcessor
from lego.apps.tags.models import Tag
from lego.apps.users.models import AbakusGroup
from lego.utils.tasks import AbakusTask

log = get_logger()


def add_source_to_url(url):
    return f"{url}?utm_source=WeeklyMail&utm_campaign=Email"


def create_weekly_mail(user):
    week_number = timezone.now().isocalendar().week

    three_days_ago_timestamp = timezone.now() - timedelta(days=3)
    last_sunday_timestamp = timezone.now() - timedelta(days=7)

    weekly_tag = Tag.objects.filter(tag="weekly").first()
    # Check if weekly tag exists so it does not crash if some idiot deletes the weekly tag
    todays_weekly = (
        weekly_tag.article_set.filter(created_at__gt=three_days_ago_timestamp).first()
        if weekly_tag
        else None
    )

    events_next_week = Event.objects.filter(
        pools__activation_date__gt=timezone.now(),
        pools__activation_date__lt=timezone.now() + timedelta(days=7),
    ).distinct()

    permission_handler = get_permission_handler(events_next_week.model)
    filtered_events = permission_handler.filter_queryset(user, events_next_week)

    filtered_events = filter(
        lambda event: event.get_possible_pools(user, True) or event.is_admitted(user),
        filtered_events,
    )

    joblistings_last_week = Joblisting.objects.filter(
        created_at__gt=last_sunday_timestamp, visible_from__lt=timezone.now()
    )

    joblistings = []
    for joblisting in joblistings_last_week:
        joblistings.append(
            {
                "id": joblisting.id,
                "company_name": joblisting.company.name,
                "type": JOB_TYPE_TRANSLATIONS[joblisting.job_type],
                "title": joblisting.title,
            }
        )

    events = []
    for event in filtered_events:
        pools = []
        for pool in event.pools.all():
            pools.append(
                {
                    "name": pool.name,
                    "activation_date": pool.activation_date.astimezone(
                        ZoneInfo("Europe/Oslo")
                    ).strftime("%d.%m kl. %H:%M"),
                }
            )

        events.append(
            {
                "title": event.title,
                "id": event.id,
                "pools": pools,
                "start_time": event.start_time.astimezone(
                    ZoneInfo("Europe/Oslo")
                ).strftime("%d.%m kl %H:%M"),
                "url": add_source_to_url(event.get_absolute_url()),
                "type": EVENT_TYPE_TRANSLATIONS[event.event_type],
            }
        )

    html_body = render_to_string(
        "email/email/weekly_mail.html",
        {
            "week_number": week_number,
            "events": events,
            "todays_weekly": (
                ""
                if todays_weekly is None
                else add_source_to_url(todays_weekly.get_absolute_url())
            ),
            "joblistings": joblistings,
            "frontend_url": settings.FRONTEND_URL,
        },
    )
    if events or joblistings or todays_weekly:
        return html_body
    return None


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def send_weekly_email(self, logger_context=None):
    self.setup_logger(logger_context)

    week_number = timezone.now().isocalendar().week

    # Send to all active students
    all_users = set(AbakusGroup.objects.get(name="Students").restricted_lookup()[0])
    recipients = []

    for user in all_users:
        if not user.email_lists_enabled:
            # Don't send emails to users that don't want mail.
            continue

        if EMAIL not in NotificationSetting.active_channels(user, WEEKLY_MAIL):
            continue
        recipients.append(user)

    datatuple = (
        (
            f"Ukesmail uke {week_number}",
            transform(html) if (html := create_weekly_mail(user)) is not None else None,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        for user in recipients
    )
    datatuple = tuple(tuppel for tuppel in datatuple if tuppel[1] is not None)
    if datatuple:
        MessageProcessor.send_mass_mail_html(datatuple)
