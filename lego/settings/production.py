import os

import environ
import raven

from lego.settings import BASE_DIR, CHANNEL_LAYERS, INSTALLED_APPS, MIDDLEWARE_CLASSES

from .secure import *  # noqa

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['api.abakus.no']),
)
environ.Env.read_env(os.path.join(os.path.dirname(BASE_DIR), '.env'))


DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Database
DATABASES = {
    'default': env.db()
}

# Cache
CACHES = {
    'default': env.cache()
}

# Email / We may enable the celery email backend.
EMAIL_CONFIG = env.email()
vars().update(EMAIL_CONFIG)

# Sentry
SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
SENTRY_DSN = env('SENTRY')
RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': raven.fetch_git_sha(os.path.dirname(BASE_DIR)),
}
INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
]
MIDDLEWARE_CLASSES = [
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
] + MIDDLEWARE_CLASSES

# Celery
BROKER_URL = env('CELERY_BROKER_URL')

# Stream Framework
STREAM_REDIS_CONFIG = {
    'default': {
        'host': env('REDIS_STREAM_HOST'),
        'port': env('REDIS_STREAM_PORT'),
        'db': env('REDIS_STREAM_DB'),
        'password': env('REDIS_STREAM_PASSWORD')
    }
}

# Doppins
CHANNEL_LAYERS['default']['CONFIG'] = {
    'hosts': [env('CHANNELS_REDIS_URL')]
}

# Statsd
STATSD_CLIENT = 'django_statsd.clients.normal'
