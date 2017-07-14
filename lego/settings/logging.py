import socket
from logging import getLogger

import cssutils
import structlog
from structlog.threadlocal import wrap_dict

from lego.settings import TESTING


def skip_if_testing(*args, **kwargs):
    return not TESTING


hostname = socket.gethostname()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'syslog'],
    },
    'filters': {
        'skip_if_testing': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_if_testing,
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s [%(name)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['skip_if_testing', 'require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'syslog': {
            'level': 'INFO',
            'filters': ['skip_if_testing', 'require_debug_false'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'celery': {
            'level': 'DEBUG',
            'propagate': True,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django': {
            'level': 'DEBUG',
            'propagate': True,
            'filters': ['require_debug_true'],
        },
        'django.requests': {
            'level': 'INFO',
            'propagate': True,
            'filters': ['require_debug_true'],
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'elasticsearch': {
            'level': 'WARNING',
            'propagate': True
        },
        'botocore': {
            'level': 'WARNING',
            'propagate': True
        },
        'boto3': {
            'level': 'WARNING',
            'propagate': True
        },
        'cssutils': {
            'level': 'CRITICAL',
            'propagate': True
        }
    },
}


WrappedDictClass = wrap_dict(dict)


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=WrappedDictClass,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


cssutils_log = getLogger('cssutils')
cssutils.log.setLog(cssutils_log)
