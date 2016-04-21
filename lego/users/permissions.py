from lego.permissions.permissions import AbakusPermissions
from lego.users.models import Membership


def can_retrieve_user(user, retriever):
    required_permission = '/sudo/admin/users/retrieve/'
    return user == retriever or retriever.has_perm(required_permission)


def can_retrieve_abakusgroup(group, retriever):
    required_permission = '/sudo/admin/groups/retrieve/'
    return group in retriever.all_groups or retriever.has_perm(required_permission)


class UsersPermissions(AbakusPermissions):
    perms_map = {
        'list': ['/sudo/admin/users/list/'],
        'retrieve': None,
        'create': ['/sudo/admin/users/create/'],
        'update': ['/sudo/admin/users/update/'],
        'partial_update': ['/sudo/admin/users/update/'],
        'destroy': ['/sudo/admin/users/destroy/'],
    }

    allowed_individual = ['retrieve', 'update', 'partial_update']

    def is_self(self, request, view, obj):
        if view.action in self.allowed_individual and obj == request.user:
            return True

    def has_permission(self, request, view):
        return True if view.action in self.OBJECT_METHODS else super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if self.is_self(request, view, obj):
            return True
        return super().has_object_permission(request, view, obj)


class AbakusGroupPermissions(AbakusPermissions):
    perms_map = {
        'list': None,
        'hierarchy': None,
        'retrieve': None,
        'create': ['/sudo/admin/groups/create/'],
        'update': ['/sudo/admin/groups/update/'],
        'partial_update': ['/sudo/admin/groups/update/'],
        'destroy': ['/sudo/admin/groups/destroy/'],
    }

    allowed_leader = ['update', 'partial_update']

    def has_permission(self, request, view):
        return True if view.action in self.allowed_leader else super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action in self.allowed_leader:
            user = request.user
            is_owner = bool(Membership.objects.filter(abakus_group=obj, user=user,
                                                      role=Membership.LEADER))
            return is_owner or super().has_object_permission(request, view, obj)

        return super().has_object_permission(request, view, obj)
