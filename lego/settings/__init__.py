# -*- coding: utf8 -*-
from lego.settings.base import *

if 'compressor' in INSTALLED_APPS:
    from lego.settings.compress import *

# Import local settings like DB passwords and SECRET_KEY
try:
    from lego.settings.local import *
except ImportError as e:
    raise ImportError("Couldn't load local settings lego.settings.local")

if 'debug_toolbar' in INSTALLED_APPS:
    from lego.settings.debug_toolbar import *

from lego.settings.logging import LOGGING
