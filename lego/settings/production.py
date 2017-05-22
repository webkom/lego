import os
from urllib.parse import urlparse

import environ
import stripe
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
FRONTEND_URL = env('FRONTEND_URL')
SERVER_EMAIL = env('SERVER_EMAIL', default='Abakus Webkom <webkom@abakus.no>')

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

# Stripe
stripe.api_key = env('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# Captcha
CAPTCHA_KEY = env('CAPTCHA_KEY')

# LDAP
LDAP_SERVER = env('LDAP_SERVER')
LDAP_USER = env('LDAP_USER')
LDAP_PASSWORD = env('LDAP_PASSWORD')

# STATSD
STATSD_HOST = env('STATSD_HOST')
STATSD_PORT = env('STATSD_PORT')
STATSD_PREFIX = env('STATSD_PREFIX', default='lego_prod')

# CORS
CORS_ORIGIN_WHITELIST = list({
    urlparse(FRONTEND_URL).netloc,
    '127.0.0.1:3000',
    'localhost:3000'
})
