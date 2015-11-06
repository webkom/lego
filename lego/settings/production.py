import json
import os

import raven

from lego.settings import BASE_DIR

DEBUG = False
ALLOWED_HOSTS = ['.abakus.no']

with open(os.path.join(BASE_DIR, '../.configuration.json')) as production_settings:
    production_values = json.loads(production_settings.read())

ADMINS = (
    ('Webkom', 'djangoerrors@abakus.no'),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': production_values.get('MEMCACHED_SERVER', '127.0.0.1:11211'),
        'KEY_PREFIX': '/lego-production',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': production_values.get('DATABASE_NAME', 'lego'),
        'USER': production_values.get('DATABASE_USER', 'lego'),
        'PASSWORD': production_values.get('DATABASE_PASSWORD'),
        'HOST': production_values.get('DATABASE_HOST', '127.0.0.1'),
        'PORT': production_values.get('DATABASE_PORT', 5432),
        'CONN_MAX_AGE': 300,
        'OPTIONS': {
            'autocommit': True,
        },
    }
}

# Lego is under development. "Production" is only a test environment and we don't want it to send
#  mail by accident.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOG_PRINT_LEVEL = 1

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECRET_KEY = production_values['SECRET_KEY']

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)


SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
RAVEN_CONFIG = {
    'dsn': production_values.get('SENTRY_DSN'),
    'release': raven.fetch_git_sha(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
}

BROKER_URL = production_values['CELERY_BROKER']
