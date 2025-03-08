from lego.apps.permissions.constants import LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class FeatureFlagsPermissionHandler(PermissionHandler):
    safe_methods = [LIST, VIEW]
