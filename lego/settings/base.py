import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'This is supersecret'

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

    'rest_framework',
    'mptt',

    'lego.apps.LegoConfig',
    'lego.users',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

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
