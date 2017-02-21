from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.permissions.permissions import AbakusPermission
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, Membership, User


def can_retrieve_user(user, retriever):
    return user == retriever or retriever.has_perm('users.user.can_retrieve')


def can_retrieve_abakusgroup(group, retriever):
    return group in retriever.all_groups or retriever.has_perm('users.abakusgroup.can_retrieve')


class UsersPermissionIndex(PermissionIndex):

    queryset = User.objects.all()

    list = (['/sudo/admin/users/list/'], 'can_view')
    retrieve = ([], None)
    create = (['/sudo/admin/users/create/'], None)
    update = (['/sudo/admin/users/update/'], 'can_edit')
    partial_update = (['/sudo/admin/users/update/'], 'can_edit')
    destroy = (['/sudo/admin/users/destroy/'], 'can_edit')

    can_retrieve = (['/sudo/admin/users/retrieve/'], 'can_view')


class GroupPermissionIndex(PermissionIndex):

    queryset = AbakusGroup.objects.all()

    list = ([], None)
    retrieve = ([], None)
    create = (['/sudo/admin/groups/create/'], None)
    update = (['/sudo/admin/groups/update/'], 'can_edit')
    partial_update = (['/sudo/admin/groups/update/'], 'can_edit')
    destroy = (['/sudo/admin/groups/destroy/'], 'can_edit')

    can_retrieve = (['/sudo/admin/groups/retrieve/'], 'can_view')


register(UsersPermissionIndex)
register(GroupPermissionIndex)


class UsersPermissions(AbakusPermission):

    allowed_individual = ['retrieve', 'update', 'partial_update']

    def is_self(self, request, view, obj):
        if view.action in self.allowed_individual and obj == request.user:
            return True

    def has_permission(self, request, view):
        if view.action in self.OBJECT_METHODS:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if self.is_self(request, view, obj):
            return True
        return super().has_object_permission(request, view, obj)


class AbakusGroupPermissions(AbakusPermission):

    allowed_leader = ['update', 'partial_update']

    def has_permission(self, request, view):
        if view.action in self.allowed_leader:
            return True

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action in self.allowed_leader and request.user.is_authenticated():
            user = request.user
            is_owner = Membership.objects.filter(
                abakus_group=obj, user=user, role=constants.LEADER
            ).exists()
            return is_owner or super().has_object_permission(request, view, obj)

        return super().has_object_permission(request, view, obj)
