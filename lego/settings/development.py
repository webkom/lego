import os

import stripe

from .base import INSTALLED_APPS, MIDDLEWARE_CLASSES
from .rest_framework import REST_FRAMEWORK

DEBUG = True
DEVELOPMENT = True

SERVER_URL = 'http://127.0.0.1:8000'

SECRET_KEY = 'secret'
stripe.api_key = os.environ.get('STRIPE_TEST_KEY')

WEBHOOK_USERNAME = 'stripe'
WEBHOOK_PASSWORD = 'webhook'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'NAME': 'lego',
        'USER': 'lego',
        'PASSWORD': '',
        'PORT': '',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = ['127.0.0.1']
INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE_CLASSES = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE_CLASSES
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += ['rest_framework.renderers.BrowsableAPIRenderer']

CELERY_BROKER_URL = 'redis://127.0.0.1'

STREAM_REDIS_CONFIG = {
    'default': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
        'password': None
    },
}

ELASTICSEARCH = [
    {'host': '127.0.0.1'},
]

CELERY_TASK_ALWAYS_EAGER = True
