import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'This is supersecret'

TESTING = 'test' in sys.argv  # Check if manage.py test has been run

SHELL_PLUS = 'ipython'

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'oauth2_provider',
    'rest_framework',

    'lego.apps.LegoConfig',
    'lego.users',
    'lego.app.mail',

    'lego.app.oauth',
)

AUTHENTICATION_BACKEND = (
    'oauth2_provider.backends.OAuth2Backend'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth.APIApplication'

ROOT_URLCONF = 'lego.urls'

WSGI_APPLICATION = 'lego.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEBUG = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static')
MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../uploads')

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)
