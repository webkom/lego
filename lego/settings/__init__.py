import os
import sys

TESTING = 'test' in sys.argv[:2]
DAPHNE_SERVER = 'daphne' in sys.argv

from .base import *  # noqa
from .lego import *  # noqa
from .rest_framework import *  # noqa
from .search import *  # noqa
from .logging import *  # noqa

if TESTING:
    from .test import *  # noqa
else:

    if os.environ.get('ENV_CONFIG') in ['1', 'True', 'true']:
        from .production import *  # noqa
    else:
        try:
            from .local import *  # noqa
        except ImportError as e:
            raise ImportError('Couldn\'t load local settings lego.settings.local')

DEFAULT_FROM_EMAIL = SERVER_EMAIL  # noqa
