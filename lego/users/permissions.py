from lego.permissions.keyword_permissions import KeywordPermissions
from lego.users.models import Membership


def can_retrieve_user(user, retriever):
    required_permission = '/sudo/admin/users/retrieve/'
    return user == retriever or retriever.has_perm(required_permission)


def can_retrieve_abakusgroup(group, retriever):
    required_permission = '/sudo/admin/groups/retrieve/'
    return group in retriever.all_groups or retriever.has_perm(required_permission)


class UsersPermissions(KeywordPermissions):
    perms_map = {
        'list': '/sudo/admin/users/list/',
        'retrieve': None,
        'create': '/sudo/admin/users/create/',
        'update': '/sudo/admin/users/update/',
        'partial_update': '/sudo/admin/users/update/',
        'destroy': '/sudo/admin/users/destroy/',
    }

    allowed_individual = ['retrieve', 'update', 'partial_update']

    def has_object_permission(self, request, view, obj):
        if view.action in self.allowed_individual and obj == request.user:
            return True

        return super().has_object_permission(request, view, obj)


class AbakusGroupPermissions(KeywordPermissions):
    perms_map = {
        'list': None,
        'retrieve': None,
        'create': '/sudo/admin/groups/create/',
        'update': '/sudo/admin/groups/update/',
        'partial_update': '/sudo/admin/groups/update/',
        'destroy': '/sudo/admin/groups/destroy/',
    }

    allowed_leader = ['update', 'partial_update']

    def has_object_permission(self, request, view, obj):
        if view.action in self.allowed_leader:
            user = request.user
            is_owner = bool(Membership.objects.filter(abakus_group=obj, user=user,
                                                      role=Membership.LEADER))
            return is_owner or super().has_object_permission(request, view, obj)

        return super().has_object_permission(request, view, obj)
