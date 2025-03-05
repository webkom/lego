from lego.apps.permissions.constants import LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class BannersPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/banners/{perm}/"

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        if perm == LIST:
            return True
        if perm == VIEW:
            return True

        return super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )
