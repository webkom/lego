from .base import INSTALLED_APPS
from .rest_framework import REST_FRAMEWORK

DEBUG = False

SECRET_KEY = 'secret'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'NAME': 'lego'
    }
}

INSTALLED_APPS += ('lego.permissions.tests',)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

STREAM_REDIS_CONFIG = {
    'default': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 10,
        'password': None
    },
}

# We don't care about pagination in the tests
REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = None

STATSD_CLIENT = 'django_statsd.clients.null'
STATSD_PATCHES = []
STATSD_MODEL_SIGNALS = False
STATSD_CELERY_SIGNALS = False

ELASTICSEARCH = [
    {'host': 'localhost'},
]

CELERY_ALWAYS_EAGER = True
