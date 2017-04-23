from __future__ import absolute_import

import os

import celery  # noqa
from cassandra.cqlengine import connection
from cassandra.cqlengine.connection import cluster as cql_cluster
from cassandra.cqlengine.connection import session as cql_session
from celery.schedules import crontab
from celery.signals import beat_init, eventlet_pool_started, worker_process_init
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lego.settings')


@eventlet_pool_started.connect()
@worker_process_init.connect()
@beat_init.connect()
def cassandra_init(*args, **kwargs):
    """
    Initialize a clean Cassandra connection.
    """
    if cql_cluster is not None:
        cql_cluster.shutdown()
    if cql_session is not None:
        cql_session.shutdown()
    connection.setup(
        hosts=settings.STREAM_CASSANDRA_HOSTS,
        consistency=settings.STREAM_CASSANDRA_CONSISTENCY_LEVEL,
        default_keyspace=settings.STREAM_DEFAULT_KEYSPACE,
        **settings.CASSANDRA_DRIVER_KWARGS
    )


class Celery(celery.Celery):
    def on_configure(self):

        import raven
        from raven.contrib.celery import register_signal, register_logger_signal

        client = raven.Client()

        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)

        # hook into the Celery error handler
        register_signal(client)


app = celery.Celery('lego')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
schedule = {
    'check-for-bump-after-penalty-expiration': {
        'task': 'lego.apps.events.tasks.check_events_for_registrations_with_expired_penalties',
        'schedule': crontab(minute='*/5')
    },
    'bump-users-to-new-pools-before-activation': {
        'task': 'lego.apps.events.tasks.bump_waiting_users_to_new_pool',
        'schedule': crontab(minute='*/30')
    },
    'notify_user_when_payment_overdue': {
        'task': 'lego.apps.events.tasks.notify_user_when_payment_overdue',
        'schedule': crontab(hour='0')
    },
    'notify_creator_when_payment_overdue': {
        'task': 'lego.apps.events.tasks.run_notify_creator_chain',
        'schedule': crontab(hour='0')
    },
    'sync-external-systems': {
        'task': 'lego.apps.external_sync.tasks.sync_external_systems',
        'schedule': crontab(minute='*/15')
    }
}

app.conf.update(
    beat_schedule=schedule,
    result_backend=None,
    task_track_started=True,
    task_serializer='pickle',
    worker_disable_rate_limits=True,
    task_ignore_result=True,
    task_acks_late=False,
    worker_hijack_root_logger=False,
    worker_redirect_stdouts=False,
    accept_content=['pickle', 'json']
)
