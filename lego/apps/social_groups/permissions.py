from lego.apps.permissions.constants import EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.users.constants import MEMBER


class InterestGroupPermissionHandler(PermissionHandler):
    permission_map = {
        LIST: [],
        VIEW: []
    }

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
