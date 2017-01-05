from lego.apps.permissions.permissions import AbakusPermission


class PagePermissions(AbakusPermission):
    # Turn off permission checks for read-only:
    permission_map = {
        'list': [],
        'retrieve': []
    }

    authentication_map = {
        'list': False,
        'retrieve': False
    }
