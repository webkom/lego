from channels.handler import AsgiHandler
from channels.routing import include, route
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status

from lego.apps.websockets.handlers import handle_connect, handle_disconnect, handle_message


def http_consumer(message):
    # Make standard HTTP response - access ASGI path attribute directly
    response = HttpResponse(status=status.HTTP_403_FORBIDDEN)
    # Encode that response into message format (ASGI)
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


websocket_routes = [
    route('websocket.receive', handle_message),
    route('websocket.connect', handle_connect),
    route('websocket.disconnect', handle_disconnect)
]

routing = [
    include(websocket_routes)
]

if settings.WS_SERVER:
    routing.append(route('http.request', http_consumer))
