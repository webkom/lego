import sys

TESTING = 'test' in sys.argv[:2]  # Check if manage.py test has been run

from .base import *  # noqa
from .lego import *  # noqa
from .rest_framework import *  # noqa
from .search import *  # noqa
from .logging import *  # noqa

if TESTING:
    from .test import *  # noqa
else:
    try:
        from .local import *  # noqa
    except ImportError as e:
        raise ImportError("Couldn't load local settings lego.settings.local")
