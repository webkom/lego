from django.conf import settings
from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
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

    async def __call__(self, scope):
        log.warn("http_disabled_daphne")
        raise ValueError


protocols = {
    "websocket": JWTAuthenticationMiddleware(
        URLRouter([url("^$", GroupConsumer.as_asgi())])
    )
}

if settings.DAPHNE_SERVER:
    protocols["http"] = HTTPConsumer

application = ProtocolTypeRouter(protocols)
