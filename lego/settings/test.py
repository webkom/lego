from .base import INSTALLED_APPS

DEBUG = False
TESTING = True

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

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
