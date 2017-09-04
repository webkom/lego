from lego.apps.permissions.constants import LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class JoblistingPermissionHandler(PermissionHandler):

    authentication_map = {
        LIST: False,
        VIEW: False
    }
