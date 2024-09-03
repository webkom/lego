from lego.apps.permissions.constants import CREATE, DELETE, EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.users import constants

EDIT_ROLES = (constants.LEADER, constants.CO_LEADER)


class LendableObjectPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendableobjects/{perm}/"
