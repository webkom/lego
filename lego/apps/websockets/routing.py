from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.conf.urls import url
from structlog import get_logger

from lego.apps.websockets.auth import JWTAuthenticationMiddleware
from lego.apps.websockets.consumers import GroupConsumer

log = get_logger()


class HTTPConsumer:
    """
    The HTTPConsumer disables the http protocol when the application is running in production.
    Http is handled by uwsgi in production.
    """

    def __init__(self, *args, **kwargs):
        pass

    async def __call__(self, receive, send):
        log.warn('http_disabled_daphne')
        raise ValueError


protocols = {
    'websocket': JWTAuthenticationMiddleware(URLRouter([
        url("^$", GroupConsumer),
    ])),
}

if settings.WS_SERVER:
    protocols['http'] = HTTPConsumer

application = ProtocolTypeRouter(protocols)
