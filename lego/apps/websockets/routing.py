from channels import include, route

from lego.apps.websockets.handlers import handle_connect, handle_disconnect

websocket_routes = [
    route('websocket.connect', handle_connect),
    route('websocket.disconnect', handle_disconnect)
]

routing = [
    include(websocket_routes)
]
