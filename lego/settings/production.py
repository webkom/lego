# -*- coding: utf8 -*-
import os

DEBUG = False
ALLOWED_HOSTS = ['.abakus.no']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'legoprod'
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
        'OPTIONS': {
            'autocommit': True,
        },

    }
}

EMAIL_HOST = 'smtp.stud.ntnu.no'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

LOG_PRINT_LEVEL = 1

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECRET_KEY = os.environ['SECRET_KEY']
