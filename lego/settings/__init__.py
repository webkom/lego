# -*- coding: utf8 -*-
from lego.settings.base import *
from lego.settings.lego import *

if 'compressor' in INSTALLED_APPS:
    from lego.settings.compress import *

if 'rest_framework' in INSTALLED_APPS:
    from lego.settings.rest_framework import *

# Import local settings like DB passwords and SECRET_KEY
try:
    from lego.settings.local import *
except ImportError as e:
    raise ImportError("Couldn't load local settings lego.settings.local")

TEMPLATE_DEBUG = DEBUG

if 'debug_toolbar' in INSTALLED_APPS:
    from lego.settings.debug_toolbar import *

from lego.settings.logging import LOGGING
