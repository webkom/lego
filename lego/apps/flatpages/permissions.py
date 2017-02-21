from lego.apps.flatpages.models import Page
from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.permissions.permissions import AbakusPermission


class PagePermissionIndex(PermissionIndex):

    queryset = Page.objects.all()

    list = ([], None)
    retrieve = ([], None)
    create = (['/sudo/admin/pages/create/'], None)
    update = (['/sudo/admin/pages/update/'], 'can_edit')
    partial_update = (['/sudo/admin/pages/update/'], 'can_edit')
    destroy = (['/sudo/admin/pages/destroy/'], 'can_edit')


register(PagePermissionIndex)


class PagePermissions(AbakusPermission):
    authentication_map = {
        'list': False,
        'retrieve': False
    }
