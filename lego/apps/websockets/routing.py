from django.core.asgi import get_asgi_application
from django.urls import re_path

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from lego.apps.websockets.auth import JWTAuthenticationMiddleware
from lego.apps.websockets.consumers import GroupConsumer

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthenticationMiddleware(
                URLRouter([re_path("^$", GroupConsumer.as_asgi())])
            )
        ),
    }
)
