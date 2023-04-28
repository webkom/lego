from django.conf import settings
from django.urls import re_path
from rest_framework import status

from channels.generic.http import AsyncHttpConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from structlog import get_logger

from lego.apps.websockets.auth import JWTAuthenticationMiddleware
from lego.apps.websockets.consumers import GroupConsumer

log = get_logger()


class HTTPConsumer(AsyncHttpConsumer):
    """
    The HTTPConsumer disables the http protocol when the application is running in production.
    Http is handled by uwsgi in production.
    """

    async def handle(self, body: bytes) -> None:
        log.warn("http_disabled_daphne")
        await self.send_response(
            status.HTTP_405_METHOD_NOT_ALLOWED,
            b"This server does not accept http",
            headers=[(b"Content-Type", b"text/plain")],
        )


protocols = {
    "websocket": JWTAuthenticationMiddleware(
        URLRouter([re_path("^$", GroupConsumer.as_asgi())])
    )
}

if settings.DAPHNE_SERVER:
    protocols["http"] = HTTPConsumer()

application = ProtocolTypeRouter(protocols)
