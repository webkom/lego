import os
from urllib.parse import urlparse

import environ
import stripe

from lego.settings import (
    BASE_DIR, CHANNEL_LAYERS, INSTALLED_APPS, MIDDLEWARE, PUSH_NOTIFICATIONS_SETTINGS
)

from .secure import *  # noqa

env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, ['api.abakus.no']))
environ.Env.read_env(os.path.join(os.path.dirname(BASE_DIR), '.env'))

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
SERVER_URL = env('SERVER_URL')
FRONTEND_URL = env('FRONTEND_URL')
SERVER_EMAIL = env('SERVER_EMAIL', default='Abakus <no-reply@abakus.no>')
ENVIRONMENT_NAME = env('ENVIRONMENT_NAME', default='production')

# Database
DATABASES = {'default': env.db()}

# Cache
CACHES = {'default': env.cache()}

# Email / We may enable the celery email backend.
EMAIL_CONFIG = env.email()
vars().update(EMAIL_CONFIG)

# File Storage
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_REGION = env('AWS_REGION')
AWS_S3_BUCKET = env('AWS_S3_BUCKET')

THUMBOR_SERVER = env('THUMBOR_SERVER')
THUMBOR_SECURITY_KEY = env('THUMBOR_SECURITY_KEY')

# Sentry
SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
SENTRY_DSN = env('SENTRY')
RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': env('RELEASE', default='latest'),
    'environment': ENVIRONMENT_NAME
}
INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
]
MIDDLEWARE = [
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
] + MIDDLEWARE

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL')

# Channels
CHANNEL_LAYERS['default']['CONFIG'] = {'hosts': [env('CHANNELS_REDIS_URL')]}

# Elasticsearch
ELASTICSEARCH = [
    {
        'host': env('ELASTICSEARCH_HOST')
    },
]
SEARCH_INDEX = env('SEARCH_INDEX', default='lego-search')

# Stripe
stripe.api_key = env('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# Captcha
CAPTCHA_KEY = env('CAPTCHA_KEY')

# LDAP
LDAP_SERVER = env('LDAP_SERVER')
LDAP_USER = env('LDAP_USER')
LDAP_PASSWORD = env('LDAP_PASSWORD')

# Analytics
ANALYTICS_HOST = env('ANALYTICS_HOST', default=None)
ANALYTICS_WRITE_KEY = env('ANALYTICS_WRITE_KEY', default='')

# CORS
CORS_FRONTEND_URL = urlparse(FRONTEND_URL).netloc
CORS_ORIGIN_WHITELIST = list(
    {CORS_FRONTEND_URL, f'www.{CORS_FRONTEND_URL}', '127.0.0.1:3000', 'localhost:3000'}
)

# Restricted
RESTRICTED_ADDRESS = env('RESTRICTED_ADDRESS', default='restricted')
RESTRICTED_DOMAIN = env('RESTRICTED_DOMAIN', default='abakus.no')
RESTRICTED_FROM = env('RESTRICTED_FROM', default='Abakus <no-reply@abakus.no>')

# Push Notifications
PUSH_NOTIFICATIONS_SETTINGS['APNS_USE_SANDBOX'] = env('APNS_USE_SANDBOX', default=False)
PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'] = env('APNS_CERTIFICATE')
PUSH_NOTIFICATIONS_SETTINGS['FCM_API_KEY'] = env('FCM_API_KEY', default=None)
PUSH_NOTIFICATIONS_SETTINGS['GCM_API_KEY'] = env('GCM_API_KEY', default=None)
