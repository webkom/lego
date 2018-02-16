from lego.apps.permissions.permissions import PermissionHandler


class QuotePermissionHandler(PermissionHandler):

    permission_map = {
        'random': [],
        'approve': ['/sudo/admin/quotes/change-approval/'],
        'unapprove': ['/sudo/admin/quotes/change-approval/'],
    }
