from lego.apps.permissions.permissions import PermissionHandler


class LendableObjectPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendableobjects/{perm}/"

class LendingRequestPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendingrequests/{perm}/"
