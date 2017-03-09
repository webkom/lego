from lego.apps.flatpages.models import Page
from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.permissions.permissions import AbakusPermission


class PagePermissionIndex(PermissionIndex):

    model = Page

    list = []
    retrieve = []
    create = ['/sudo/admin/pages/create/']
    update = ['/sudo/admin/pages/update/']
    partial_update = ['/sudo/admin/pages/update/']
    destroy = ['/sudo/admin/pages/destroy/']


register(PagePermissionIndex)


class PagePermissions(AbakusPermission):
    authentication_map = {
        'list': False,
        'retrieve': False
    }
