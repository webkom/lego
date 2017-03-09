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
    'oauth2_provider',
    'rest_framework',
    'corsheaders',
    'mptt',
    'channels',
    'django_thumbor',

    'lego.utils',
    'lego.apps.users',
    'lego.apps.permissions',
    'lego.apps.articles',
    'lego.apps.comments',
    'lego.apps.content',
    'lego.apps.events',
    'lego.apps.companies',
    'lego.apps.feed',
    'lego.apps.files',
    'lego.apps.flatpages',
    'lego.apps.followers',
    'lego.apps.social_groups',
    'lego.apps.meetings',
    'lego.apps.oauth',
    'lego.apps.search',
    'lego.apps.slack',
    'lego.apps.tags',
    'lego.apps.quotes',
    'lego.apps.reactions',
    'lego.apps.websockets',
    'lego.apps.joblistings'
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = (
    'lego.apps.permissions.backends.AbakusPermissionBackend',
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
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'lego.utils.middleware.LoggingMiddleware'
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
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'lego.apps.jwt.handlers.response_handler'
}

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth.APIApplication'
# Tokens is valid for 7 days.
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 86400 * 7,
    'SCOPES': {
        'user': 'Grants access to the user profile'
    }
}

ROOT_URLCONF = 'lego.urls'

WSGI_APPLICATION = 'lego.wsgi.application'

TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
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

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgi_redis.RedisChannelLayer',
        'ROUTING': 'lego.apps.websockets.routing.routing'
    }
}

STREAM_METRIC_CLASS = 'lego.apps.feed.feed_metrics.PrometheusFeedMetrics'
CASSANDRA_DRIVER_KWARGS = {
    'protocol_version': 4,
    'lazy_connect': True
}
