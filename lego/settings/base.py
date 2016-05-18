import datetime
import os

import environ

root = environ.Path(__file__) - 2
BASE_DIR = root()

SHELL_PLUS = 'ipython'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'djangosecure',
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
    'lego.app.feed',
    'lego.app.flatpages',
    'lego.app.comments',
]

MIGRATION_MODULES = {
    'oauth2_provider': 'lego.migrations.oauth2_provider'
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = (
    'lego.permissions.backends.KeywordPermissionBackend',
    'oauth2_provider.backends.OAuth2Backend',
)
LOGIN_URL = '/authorization/login/'
LOGOUT_URL = '/authorization/logout/'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
                'lego.utils.context_processors.site',
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

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATIC_ROOT = os.path.join(BASE_DIR, 'files', 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    ('assets', os.path.join(BASE_DIR, 'assets')),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'files', 'media')
MEDIA_URL = '/media/'

CORS_ORIGIN_ALLOW_ALL = True
