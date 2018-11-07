from lego.apps.permissions.constants import LIST
from lego.apps.permissions.permissions import PermissionHandler


class PodcastPermissionHandler(PermissionHandler):
    authentication_map = {LIST: False}
