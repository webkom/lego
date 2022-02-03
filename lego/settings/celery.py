from __future__ import absolute_import

import os

import celery  # noqa
from celery.schedules import crontab
from celery.signals import (
    beat_init,
    eventlet_pool_started,
    setup_logging,
    worker_process_init,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lego.settings")

app = celery.Celery("lego")


@eventlet_pool_started.connect()
@worker_process_init.connect()
@beat_init.connect()
def celery_init(*args, **kwargs):
    """
    Initialize a clean threads
    """
    from lego.apps.stats import analytics_client

    analytics_client.default_client = None
    analytics_client.setup_analytics()


@setup_logging.connect()
def on_setup_logging(**kwargs):
    """
    This prevents celery from tampering with our logging config.
    """
    pass


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
