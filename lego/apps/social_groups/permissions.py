from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.social_groups.models import InterestGroup
from lego.apps.users.permissions import AbakusGroupPermissions


class InterestGroupPermissionIndex(PermissionIndex):

    queryset = InterestGroup.objects.all()

    list = []
    retrieve = []
    create = ['/sudo/admin/interestgroups/create/']
    update = ['/sudo/admin/interestgroups/update/']
    partial_update = ['/sudo/admin/interestgroups/update/']
    destroy = ['/sudo/admin/interestgroups/destroy/']


register(InterestGroupPermissionIndex)


class InterestGroupPermissions(AbakusGroupPermissions):
    allowed_leader = ['update', 'partial_update']
