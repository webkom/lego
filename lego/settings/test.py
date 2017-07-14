import os

import stripe
from cassandra import ConsistencyLevel

from .base import CASSANDRA_DRIVER_KWARGS, CHANNEL_LAYERS, INSTALLED_APPS

DEBUG = False
SERVER_URL = 'http://127.0.0.1:8000'
FRONTEND_URL = 'http://127.0.0.1:8000'
SERVER_EMAIL = 'Abakus Webkom <webkom@abakus.no>'

SECRET_KEY = 'secret'
stripe.api_key = os.environ.get('STRIPE_TEST_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('DATABASE') or '127.0.0.1',
        'NAME': 'lego',
        'USER': 'lego'
    }
}

CACHE = os.environ.get('CACHE') or '127.0.0.1'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'redis://{CACHE}:6379/0',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

STREAM_CASSANDRA_HOSTS = [os.environ.get('CASSANDRA') or '127.0.0.1']
STREAM_CASSANDRA_CONSISTENCY_LEVEL = ConsistencyLevel.ONE
STREAM_DEFAULT_KEYSPACE = 'test_stream_framework'
CASSANDRA_DRIVER_KWARGS['lazy_connect'] = bool(os.environ.get('CASS_LAZY'))

STREAM_REDIS_CONFIG = {
    'default': {
        'host': CACHE,
        'port': 6379,
        'db': 10,
        'password': None
    },
}

ELASTICSEARCH = [
    {'host': 'localhost'},
]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

CHANNEL_LAYERS['default']['CONFIG'] = {
    'hosts': [f'redis://{CACHE}/5']
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

INSTALLED_APPS += ('lego.apps.permissions.tests',)

SLACK_TEAM = ''
SLACK_TOKEN = ''

LDAP_SERVER = '127.0.0.1:389'
LDAP_USER = 'cn=admin,dc=abakus,dc=no'
LDAP_PASSWORD = 'admin'
