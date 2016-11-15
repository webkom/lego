from __future__ import absolute_import

import os

import celery  # noqa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lego.settings')


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

schedule = {}

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
