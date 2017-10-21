from lego.apps.permissions.permissions import PermissionHandler


class UserEmailPermissionHandler(PermissionHandler):

    default_keyword_permission = '/sudo/admin/emailusers/{perm}/'
