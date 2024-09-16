import os

import stripe

from .base import CHANNEL_LAYERS, INSTALLED_APPS

# Disable migrations for all apps (not on CI):
if "DRONE" not in os.environ:
    MIGRATION_MODULES = {
        "auth": None,
        "contenttypes": None,
        "default": None,
        "sessions": None,
        "tests": None,
    }

    for app in INSTALLED_APPS:
        MIGRATION_MODULES[app.split(".")[-1]] = None

DEBUG = False
SERVER_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:8000"
SERVER_EMAIL = "Abakus <no-reply@abakus.no>"

SECRET_KEY = "secret"
stripe.api_key = os.environ.get("STRIPE_TEST_KEY")

CAPTCHA_KEY = os.environ.get("CAPTCHA_KEY") or "1x0000000000000000000000000000000AA"

# Work-around for a weird bug where the tests would crash with -v=3 (verbosity):
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "oauth2_provider.AccessToken"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DATABASE") or "127.0.0.1",
        "NAME": "lego",
        "USER": "lego",
    }
}

CACHE = os.environ.get("CACHE") or "127.0.0.1"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{CACHE}:6379/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    },
    "oauth": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{CACHE}:6379/9",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    },
}

ELASTICSEARCH = "localhost"
SEARCH_BACKEND = "postgres"

CELERY_TASK_ALWAYS_EAGER = True

CHANNEL_LAYERS["default"]["CONFIG"] = {"hosts": [f"redis://{CACHE}/5"]}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

INSTALLED_APPS += ("lego.apps.permissions.tests",)
INSTALLED_APPS.remove("django_extensions")
INSTALLED_APPS.remove("corsheaders")

LDAP_SERVER = "127.0.0.1:389"
LDAP_USER = "cn=admin,dc=abakus,dc=no"
LDAP_PASSWORD = "admin"
