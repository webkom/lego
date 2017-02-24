import os

import stripe

from .base import INSTALLED_APPS

DEBUG = False
SERVER_URL = 'http://127.0.0.1:8000'

SECRET_KEY = 'secret'
stripe.api_key = os.environ.get('STRIPE_TEST_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'NAME': 'lego',
        'USER': 'lego'
    }
}

INSTALLED_APPS += ('lego.apps.permissions.tests',)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
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

ELASTICSEARCH = [
    {'host': 'localhost'},
]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STREAM_DEFAULT_KEYSPACE = 'test_stream_framework'
