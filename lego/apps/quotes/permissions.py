from lego.apps.permissions.permissions import AbakusPermission


class QuotePermissions(AbakusPermission):

    permission_map = {
        'random': [],
        'approve': ['/sudo/admin/quotes/change-approval/'],
        'unapprove': ['/sudo/admin/quotes/change-approval/'],
    }
