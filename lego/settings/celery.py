from __future__ import absolute_import

import os

import celery
from django.conf import settings


class Celery(celery.Celery):
    def on_configure(self):

        import raven
        from raven.contrib.celery import register_signal, register_logger_signal

        client = raven.Client()

        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)

        # hook into the Celery error handler
        register_signal(client)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lego.settings')

app = celery.Celery('lego')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERYBEAT_SCHEDULER='djcelery.schedulers.DatabaseScheduler',
    CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend',
)
