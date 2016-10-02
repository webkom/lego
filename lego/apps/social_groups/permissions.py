from lego.apps.users.permissions import AbakusGroupPermissions


def can_retrieve_interestgroup(group, retriever):
    required_permission = '/sudo/admin/interestgroups/retrieve/'
    return group in retriever.all_groups or retriever.has_perm(required_permission)


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
