from .base import INSTALLED_APPS

DEBUG = False

SECRET_KEY = 'secret'

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

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
