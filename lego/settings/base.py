import base64
import datetime
import json
import os

import environ

root = environ.Path(__file__) - 2
BASE_DIR = root()

ALLOWED_HOSTS = ["*"]
SHELL_PLUS = "ipython"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django_extensions",
    "oauth2_provider",
    "rest_framework",
    "rest_framework_jwt",
    "rest_framework_jwt.blacklist",  # Not used, but needed to avoid db issues.
    "corsheaders",
    "mptt",
    "channels",
    "django_filters",
    "push_notifications",
    "health_check",
    "phonenumber_field",
    "lego.utils",
    "lego.apps.achievements",
    "lego.apps.user_commands",
    "lego.apps.action_handlers",
    "lego.apps.articles",
    "lego.apps.banners",
    "lego.apps.comments",
    "lego.apps.companies",
    "lego.apps.contact",
    "lego.apps.content",
    "lego.apps.email",
    "lego.apps.emojis",
    "lego.apps.events",
    "lego.apps.external_sync",
    "lego.apps.featureflags",
    "lego.apps.feeds",
    "lego.apps.files",
    "lego.apps.flatpages",
    "lego.apps.followers",
    "lego.apps.frontpage",
    "lego.apps.gallery",
    "lego.apps.healthchecks",
    "lego.apps.ical",
    "lego.apps.joblistings",
    "lego.apps.lending",
    "lego.apps.meetings",
    "lego.apps.notifications",
    "lego.apps.oauth",
    "lego.apps.permissions",
    "lego.apps.podcasts",
    "lego.apps.polls",
    "lego.apps.quotes",
    "lego.apps.reactions",
    "lego.apps.restricted",
    "lego.apps.search",
    "lego.apps.surveys",
    "lego.apps.tags",
    "lego.apps.users",
    "lego.apps.websockets",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ("lego.apps.permissions.backends.LegoPermissionBackend",)
LOGIN_URL = "/authorization/login/"
LOGOUT_URL = "/authorization/logout/"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "lego.utils.middleware.cors.CORSPatchMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "lego.utils.middleware.logging.LoggingMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "lego.utils.context_processors.site",
            ]
        },
    }
]

JWT_AUTH = {
    "JWT_RESPONSE_PAYLOAD_HANDLER": "lego.apps.jwt.handlers.response_handler",
    # Tokens will expire after 14 days
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=14),
    # Allow refresh. Tokens can be refreshed for 180 days after initial login,
    # so users must login ~twice a year
    "JWT_ALLOW_REFRESH": True,
    "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=180),
}

OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth.APIApplication"
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "oauth2_provider.AccessToken"
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = "oauth2_provider.RefreshToken"
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "oauth2_provider.IDToken"
# Tokens is valid for 7 days.
OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": 86400 * 7,
    "SCOPES": {
        "user": (
            "Enkel brukerinfo. Dette gir lesetilgang til ditt navn, "
            "brukernavn, profilbilde, epost, kjønn og dine medlemskap"
        ),
        "all": "Gir tilgang til all brukerinfo. Kan også gjøre ting som deg",
    },
}

ROOT_URLCONF = "lego.urls"

WSGI_APPLICATION = "lego.wsgi.application"

SEARCH_BACKEND = "postgres"

TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = False
USE_TZ = True

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATIC_ROOT = os.path.join(BASE_DIR, "files", "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = (("assets", os.path.join(BASE_DIR, "assets")),)

MEDIA_ROOT = os.path.join(BASE_DIR, "files", "media")
MEDIA_URL = "/media/"

ASGI_APPLICATION = "lego.apps.websockets.routing.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": ["redis://127.0.0.1:6379"]},
    }
}

LDAP_BASE_DN = "dc=abakus,dc=no"

CAPTCHA_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

PUSH_NOTIFICATIONS_SETTINGS = {
    "APNS_USE_SANDBOX": False,
    "UPDATE_ON_DUPLICATE_REG_ID": True,
    "APNS_TOPIC": "no.abakus.abakus",
    "GCM_ERROR_TIMEOUT": 30,
    "FCM_ERROR_TIMEOUT": 30,
}

GSUITE_DELEGATED_ACCOUNT = os.environ.get("GSUITE_DELEGATED_ACCOUNT")
SMTP_SSL_ENABLE = os.environ.get("SMTP_SSL_ENABLE") or False
SMTP_SSL_CERTIFICATE = os.environ.get("SMTP_SSL_CERTIFICATE")
SMTP_SSL_KEY = os.environ.get("SMTP_SSL_KEY")

FEIDE_OIDC_CLIENT_ID = os.environ.get("FEIDE_OIDC_CLIENT_ID")
FEIDE_OIDC_CLIENT_SECRET = os.environ.get("FEIDE_OIDC_CLIENT_SECRET")
FEIDE_OIDC_CONFIGURATION_ENDPOINT = os.environ.get(
    "FEIDE_OIDC_CONFIGURATION_ENDPOINT",
    "https://auth.dataporten.no/.well-known/openid-configuration",
)
FEIDE_GROUPS_ENDPOINT = "https://groups-api.dataporten.no/groups/me/groups"

if os.environ.get("GSUITE_CREDENTIALS"):
    GSUITE_CREDENTIALS = json.loads(
        base64.b64decode(os.environ.get("GSUITE_CREDENTIALS")), strict=False  # type: ignore
    )
else:
    GSUITE_CREDENTIALS = None
