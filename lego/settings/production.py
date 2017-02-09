import os

import environ
from cassandra import ConsistencyLevel

from lego.settings import BASE_DIR, CHANNEL_LAYERS, INSTALLED_APPS, MIDDLEWARE_CLASSES

from .secure import *  # noqa

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['api.abakus.no']),
    CASSANDRA_HOSTS=(list, [])
)
environ.Env.read_env(os.path.join(os.path.dirname(BASE_DIR), '.env'))


DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
SERVER_URL = env('SERVER_URL')

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

# File Storage
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_REGION = env('AWS_REGION')
AWS_S3_BUCKET = env('AWS_S3_BUCKET')

THUMBOR_SERVER = env('THUMBOR_SERVER')
THUMBOR_SECURITY_KEY = env('THUMBOR_SECURITY_KEY')

# Sentry
SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
SENTRY_DSN = env('SENTRY')
RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': env('RELEASE', default='latest')
}
INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
]
MIDDLEWARE_CLASSES = [
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
] + MIDDLEWARE_CLASSES

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL')

# Stream Framework
STREAM_CASSANDRA_HOSTS = env('CASSANDRA_HOSTS')
STREAM_CASSANDRA_CONSISTENCY_LEVEL = ConsistencyLevel.THREE
STREAM_DEFAULT_KEYSPACE = env('CASSANDRA_KEYSPACE')
STREAM_REDIS_CONFIG = {
    'default': {
        'host': env('REDIS_STREAM_HOST'),
        'port': env('REDIS_STREAM_PORT', default=6379),
        'db': env('REDIS_STREAM_DB'),
        'password': env('REDIS_STREAM_PASSWORD', default=None)
    }
}

CHANNEL_LAYERS['default']['CONFIG'] = {
    'hosts': [env('CHANNELS_REDIS_URL')]
}

# Elasticsearch
ELASTICSEARCH = [
    {'host': env('ELASTICSEARCH_HOST')},
]
