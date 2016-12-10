import os

import stripe

from .base import INSTALLED_APPS
from .rest_framework import REST_FRAMEWORK

DEBUG = False

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

# We don't care about pagination in the tests
REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = None

ELASTICSEARCH = [
    {'host': 'localhost'},
]

CELERY_TASK_ALWAYS_EAGER = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
