from lego.apps.permissions.constants import LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class PollPermissionHandler(PermissionHandler):
    authentication_map = {LIST: False}
