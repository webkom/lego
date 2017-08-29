from lego.apps.permissions.permissions import AbakusPermission


class CompanyPermissions(AbakusPermission):
    default_permission = '/sudo/admin/companies/{action}/'


class CompanyInterestPermissions(AbakusPermission):
    """
    Users should be able to create a CompanyInterest without a user.
    """

    authentication_map = {
        'create': False
    }
