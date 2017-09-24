from lego.apps.permissions.constants import EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
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

        has_perm = super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)

        if has_perm:
            return True

        if user.is_authenticated() and perm == EDIT and obj is not None:
            return obj.memberships.filter(user=user).exclude(role=MEMBER).exists()

        return False


class MembershipPermissionHandler(PermissionHandler):

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        return True
