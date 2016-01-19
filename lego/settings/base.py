import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')

SHELL_PLUS = 'ipython'

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'raven.contrib.django.raven_compat',
    'oauth2_provider',
    'rest_framework',
    'corsheaders',
    'djcelery',
    'mptt',

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

MIGRATION_MODULES = {
    'oauth2_provider': 'lego.migrations.oauth2_provider'
}

AUTHENTICATION_BACKENDS = (
    'lego.permissions.backends.KeywordPermissionBackend',
    'oauth2_provider.backends.OAuth2Backend',
)

MIDDLEWARE_CLASSES = (
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'lego.utils.json_web_tokens.response_handler'
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

CORS_ORIGIN_ALLOW_ALL = True

BROKER_URL = 'redis://127.0.0.1'
