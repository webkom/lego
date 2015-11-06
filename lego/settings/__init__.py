import sys

from lego.settings.base import *
from lego.settings.lego import *
from lego.settings.rest_framework import *

from .celery import app as celery_app

TESTING = 'test' in sys.argv  # Check if manage.py test has been run

if TESTING:
    from lego.settings.test import *
else:
    from lego.settings.logging import LOGGING

    try:
        from lego.settings.local import *
    except ImportError as e:
        raise ImportError("Couldn't load local settings lego.settings.local")
