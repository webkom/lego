import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')

SHELL_PLUS = 'ipython'

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

    'lego.users',
    'lego.utils',
    'lego.permissions',

    'lego.app.oauth',
    'lego.app.articles',
    'lego.app.content',
    'lego.app.events',
    'lego.app.flatpages',
    'lego.app.comments',
)

AUTHENTICATION_BACKENDS = (
    'lego.backends.AbakusModelBackend',
    'oauth2_provider.backends.OAuth2Backend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DATE': datetime.timedelta(days=7),
}

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth.APIApplication'

ROOT_URLCONF = 'lego.urls'

WSGI_APPLICATION = 'lego.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static')
MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../uploads')

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)
