from os import environ

from analytics import Client
from django.conf import settings
from structlog import get_logger

log = get_logger()
default_client = None
development = getattr(settings, 'DEVELOPMENT', False)


def setup_analytics():
    global default_client, development

    write_key = getattr(settings, 'ANALYTICS_WRITE_KEY', '')
    host = getattr(settings, 'ANALYTICS_HOST', 'https://api.segment.io')

    production = getattr(settings, 'ENVIRONMENT_NAME', None) == 'production'
    send = not (development or getattr(settings, 'TESTING', False)) or production

    if not default_client:
        default_client = Client(
            write_key=write_key, host=host, debug=False, on_error=None, send=send
        )


def _proxy(method, user, *args, **kwargs):
    global default_client, development

    fn = getattr(default_client, method)

    kwargs['context'] = {
        'version': environ.get('RELEASE', 'latest'),
        'system': 'lego',
        'environment':
            'development' if development else getattr(settings, 'ENVIRONMENT_NAME', 'unknown')
    }

    if user.is_authenticated:
        kwargs['user_id'] = user.id
    else:
        kwargs['anonymous_id'] = 'unknown'

    fn(*args, **kwargs)


def track(user, event, properties=None):
    _proxy('track', user, event=event, properties=properties)


def identify(user):
    traits = {}

    if user.is_authenticated:
        traits.update({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'email': user.email,
            'gender': user.gender,
        })
    else:
        log.warn('analytics_identify_unknown_user')

    _proxy('identify', user, traits=traits)
