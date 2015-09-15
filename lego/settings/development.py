# -*- coding: utf8 -*-
DEBUG = True
TEMPLATE_DEBUG = True
DEVELOPMENT = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lego',
        'USER': '',
        'PASSWORD': '',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
