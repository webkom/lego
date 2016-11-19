from lego.apps.users.permissions import AbakusGroupPermissions


class InterestGroupPermissions(AbakusGroupPermissions):
    permission_map = {
        'list': [],
        'create': ['/sudo/admin/interestgroups/create/'],
        'retrieve': [],
        'update': ['/sudo/admin/interestgroups/update/'],
        'partial_update': ['/sudo/admin/interestgroups/update/'],
        'destroy': ['/sudo/admin/interestgroups/destroy/'],
    }

    allowed_leader = ['update', 'partial_update']
