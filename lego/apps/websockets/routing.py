from channels.routing import include, route

from lego.apps.websockets.handlers import handle_connect, handle_disconnect, handle_message

websocket_routes = [
    route('websocket.receive', handle_message),
    route('websocket.connect', handle_connect),
    route('websocket.disconnect', handle_disconnect)
]

routing = [
    include(websocket_routes)
]
