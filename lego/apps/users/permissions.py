from lego.apps.permissions.constants import DELETE, EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.users import constants
from lego.apps.users.constants import MEMBER


class UserPermissionHandler(PermissionHandler):

    permission_map = {
        VIEW: []
    }

    allowed_individual = [VIEW, EDIT]
    force_object_permission_check = True

    def is_self(self, perm, user, obj):
        if user.is_authenticated() and obj is not None:
            return perm in self.allowed_individual and obj == user
        return False

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):

        is_self = self.is_self(perm, user, obj)
        if is_self:
            return True

        return super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)


class AbakusGroupPermissionHandler(PermissionHandler):

    permission_map = {
        LIST: [],
        VIEW: []
    }

    default_keyword_permission = '/sudo/admin/groups/{perm}/'
    force_object_permission_check = True

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        if perm == 'delete':
            return False
        has_perm = super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)

        if has_perm:
            return True

        if user.is_authenticated() and obj is not None:
            return obj.memberships.filter(user=user).exclude(role=MEMBER).exists()

        return False


class MembershipPermissionHandler(PermissionHandler):
    allowed_individual = [VIEW, EDIT, DELETE]
    force_object_permission_check = True

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        """
        The permissions rules of membership creation is a little convoluted.
        First off, we need to be authenticated. Then, if we are creating a membership,
        that is, joining a group, we must check that the group type is a open group,
        ie. an interest group. However, we still need to check that the user joining is
        the user logged in, or else Alice can make Bob join any interest group.

        We have decided that no user are authenticated to delete a group, so when we check
        that the user has permission to act on the group, we need to special case the delete
        case, since users should be able to delete their own membership, and leaders are
        supposed to be able to kick members of their group.
        """
        if not user.is_authenticated():
            return False

        from lego.apps.users.models import AbakusGroup

        if obj is not None:
            group = obj.abakus_group
        else:
            view = kwargs.get('view', None)
            if view is None:
                return False
            group_pk = view.kwargs['group_pk']
            group = AbakusGroup.objects.get(id=group_pk)

        if 'request' in kwargs:
            membership_user = kwargs['request'].data.get('user', None)
        else:
            membership_user = obj.user.id
        is_self = user.id == membership_user

        if perm == 'create' and group.type in constants.OPEN_GROUPS:
            return is_self
        elif perm == 'delete':
            return is_self or group.leader == user

        group_permission_handler = get_permission_handler(AbakusGroup)
        has_perm = perm == group_permission_handler.has_perm(
            user, 'edit', obj=group, queryset=AbakusGroup.objects.none()
        ) or group_permission_handler.keyword_permission(group, 'edit')

        return has_perm or perm in self.safe_methods or is_self
