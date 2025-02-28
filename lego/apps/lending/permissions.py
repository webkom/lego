from lego.apps.permissions.constants import CREATE, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from django.apps import apps


class LendableObjectPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendableobjects/{perm}/"


class LendingRequestPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendingrequests/{perm}/"

