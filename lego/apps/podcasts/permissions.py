from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.permissions.constants import LIST, VIEW


class PodcastPermissionHandler(PermissionHandler):
    authentication_map = {LIST: False, VIEW: False}