# -*- coding: utf8 -*-
DEBUG = False
ALLOWED_HOSTS = ['.abakus.no']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'legoprod'
    }
}

with open('/home/webkom/webapps/passwords/lego_db', 'rb') as f:
    db_password = f.readline()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lego',
        'USER': 'lego',
        'PASSWORD': db_password.strip(),
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
