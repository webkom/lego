# -*- coding: utf8 -*-
from lego.settings.base import *
from lego.settings.lego import *
from lego.settings.rest_framework import *

if TESTING:
    from lego.settings.test import *
else:
    from lego.settings.logging import LOGGING

try:
    from lego.settings.local import *
except ImportError as e:
    raise ImportError("Couldn't load local settings lego.settings.local")

if 'debug_toolbar' in INSTALLED_APPS:
    from lego.settings.debug_toolbar import *

