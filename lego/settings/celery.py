from __future__ import absolute_import

import os

from celery.app import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lego.settings")

app = Celery("lego")


app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
schedule = {
    "check-for-bump-after-penalty-expiration": {
        "task": "lego.apps.events.tasks.check_events_for_registrations_with_expired_penalties",
        "schedule": crontab(minute="*/5"),
    },
    "bump-users-to-new-pools-before-activation": {
        "task": "lego.apps.events.tasks.bump_waiting_users_to_new_pool",
        "schedule": crontab(minute="*/30"),
    },
    "notify_user_when_payment_soon_overdue": {
        "task": "lego.apps.events.tasks.notify_user_when_payment_soon_overdue",
        "schedule": crontab(hour=9, minute=0),
    },
    "notify_event_creator_when_payment_overdue": {
        "task": "lego.apps.events.tasks.notify_event_creator_when_payment_overdue",
        "schedule": crontab(hour=9, minute=0),
    },
    "handle_overdue_payment": {
        "task": "lego.apps.events.tasks.handle_overdue_payment",
        "schedule": crontab(hour=21, minute=0),
    },
    "sync-external-systems": {
        "task": "lego.apps.external_sync.tasks.sync_external_systems",
        "schedule": crontab(hour="*", minute=0),
    },
    "check-that-pool-counters-match-registration-number": {
        "task": "lego.apps.events.tasks.check_that_pool_counters_match_registration_number",
        "schedule": crontab(hour="*", minute=0),
    },
    "notify_user_about_new_survey": {
        "task": "lego.apps.surveys.tasks.send_survey_mail",
        "schedule": crontab(minute="*/10"),
    },
    "notify_user_before_event_opens": {
        "task": "lego.apps.followers.tasks.send_registration_reminder_mail",
        "schedule": crontab(minute="*/30"),
    },
    "set_all_events_ready_and_bump": {
        "task": "lego.apps.events.tasks.set_all_events_ready_and_bump",
        "schedule": crontab(hour=4, minute=0),
    },
    "notify_inactive_user": {
        "task": "lego.apps.users.tasks.send_inactive_reminder_mail_and_delete_users",
        "schedule": crontab(hour=7, minute=0, day_of_week=1),
    },
    "notify_user_of_unanswered_meeting_invitation": {
        "task": "lego.apps.meetings.tasks.notify_user_of_unanswered_meeting_invitation",
        "schedule": crontab(hour=10, minute=0),
    },
    "send_weekly_email": {
        "task": "lego.apps.email.tasks.send_weekly_email",
        "schedule": crontab(hour=19, minute=0, day_of_week=0),
    },
    "run_check_all_promotions_weekly": {
        "task": "lego.apps.achievements.tasks.run_all_promotions",
        "schedule": crontab(hour=4, minute=0, day_of_week=0),
    },
    "generate_weekly_recurring_meetings": {
        "task": "lego.apps.meetings.tasks.generate_weekly_recurring_meetings",
        "schedule": crontab(hour=0, minute=0),
    },
}

app.conf.update(
    beat_schedule=schedule,
    result_backend=None,
    task_track_started=True,
    task_serializer="json",
    worker_disable_rate_limits=True,
    task_ignore_result=True,
    task_acks_late=False,
    worker_hijack_root_logger=False,
    worker_redirect_stdouts=False,
    accept_content=["json"],
)
