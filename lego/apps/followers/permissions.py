from lego.apps.permissions.constants import CREATE, LIST
from lego.apps.permissions.permissions import PermissionHandler


class FollowersPermissionHandler(PermissionHandler):

    default_keyword_permission = '/sudo/admin/followers/{perm}'
    force_object_permission_check = True

    permission_map = {
        CREATE: []
    }

    def filter_queryset(self, user, queryset, **kwargs):
        if user.is_authenticated():
            return queryset.filter(follower=user)
        return queryset.none()

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        if not user.is_authenticated():
            return False

        has_perm = super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)

        if has_perm:
            return True

        if self.is_authenticated(user):

            if perm == LIST:
                return True

            elif obj is not None:
                return obj.follower == user

        return False
