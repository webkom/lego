from lego.apps.permissions.permissions import AbakusPermission


class JoblistingsPermissions(AbakusPermission):
        authentication_map = {'list': False, 'retrieve': False}
