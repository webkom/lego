from lego.apps.permissions.constants import LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class PollPermissionHandler(PermissionHandler):
    permission_map: dict[str, list] = {LIST: [], VIEW: []}
