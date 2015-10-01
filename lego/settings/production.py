import os

import raven

DEBUG = False
ALLOWED_HOSTS = ['.abakus.no']

ADMINS = (
    ('Django Errors', 'djangoerrors@abakus.no'),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'legoprod',
        'TIMEOUT': 604800,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lego',
        'USER': 'lego',
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': '129.241.208.149',
        'PORT': '',
        'CONN_MAX_AGE': 300,
        'OPTIONS': {
            'autocommit': True,
        },

    }
}

EMAIL_HOST = 'smtp.stud.ntnu.no'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

LOG_PRINT_LEVEL = 1

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECRET_KEY = os.environ['SECRET_KEY']

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)


SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
RAVEN_CONFIG = {
    'dsn': os.environ['RAVEN_DSN'],
    'release': raven.fetch_git_sha(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
}
