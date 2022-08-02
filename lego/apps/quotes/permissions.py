from lego.apps.permissions.permissions import PermissionHandler


class QuotePermissionHandler(PermissionHandler):

    permission_map: dict[str, list] = {
        "random": [],
        "approve": ["/sudo/admin/quotes/change-approval/"],
        "unapprove": ["/sudo/admin/quotes/change-approval/"],
    }
