from lego.apps.permissions.permissions import AbakusPermission


class CompanyPermissions(AbakusPermission):
    default_permission = '/sudo/admin/companies/{action}/'
