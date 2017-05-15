import os
import sys
from urllib.parse import urlparse

TESTING = 'test' in sys.argv[:2]
WS_SERVER = 'runworker' in sys.argv or 'daphne' in sys.argv

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

CORS_ORIGIN_WHITELIST = list({
    urlparse(FRONTEND_URL).netloc,
    '127.0.0.1:3000',
})
