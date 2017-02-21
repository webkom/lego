from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.social_groups.models import InterestGroup
from lego.apps.users.permissions import AbakusGroupPermissions


class InterestGroupPermissionIndex(PermissionIndex):

    queryset = InterestGroup.objects.all()

    list = ([], None)
    retrieve = ([], None)
    create = (['/sudo/admin/interestgroups/create/'], None)
    update = (['/sudo/admin/interestgroups/update/'], 'can_edit')
    partial_update = (['/sudo/admin/interestgroups/update/'], 'can_edit')
    destroy = (['/sudo/admin/interestgroups/destroy/'], 'can_edit')


register(InterestGroupPermissionIndex)


class InterestGroupPermissions(AbakusGroupPermissions):
    allowed_leader = ['update', 'partial_update']
