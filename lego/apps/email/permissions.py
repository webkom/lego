from lego.apps.permissions.permissions import AbakusPermission


class UserEmailPermissions(AbakusPermission):

    default_permission = '/sudo/admin/emailusers/{action}/'


class AbakusGroupEmailPermissions(AbakusPermission):

    default_permission = '/sudo/admin/emailgroups/{action}/'
