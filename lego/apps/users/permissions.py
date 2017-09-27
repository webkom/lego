from lego.apps.permissions.constants import EDIT, LIST, VIEW, DELETE
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
        if not user.is_authenticated():
            return False

        from lego.apps.users.models import AbakusGroup

        if obj is not None:
            group = obj.group
        else:
            view = kwargs.get('view', None)
            if view is None:
                return False

            group_pk = view.kwargs['group_pk']
            group = AbakusGroup.objects.get(id=group_pk)

        if perm == 'create' and group.type in constants.OPEN_GROUPS:
            return True

        group_permission_handler = get_permission_handler(AbakusGroup)
        has_perm = group_permission_handler.has_perm(
            user, perm, obj=group, queryset=AbakusGroup.objects.none()
        )

        membership_user = kwargs['request'].data['user']
        return has_perm or perm in self.safe_methods or membership_user == user
