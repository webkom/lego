from lego.apps.permissions.constants import CREATE, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler


class LendableObjectPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendableobjects/{perm}/"

    safe_methods = [VIEW, LIST, "availability"]


class LendingRequestPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendingrequests/{perm}/"
    force_object_permission_check = True
    default_require_auth = True

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        if not user.is_authenticated:
            return False

        if obj is not None:
            if self.has_object_permissions(user, perm, obj):
                return True
        if perm is LIST or perm is VIEW or perm is CREATE:
            return True

        return super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )

    def has_object_permissions(self, user, perm, obj):
        if obj.created_by == user:
            return True
        if obj.lendable_object._meta.permission_handler.has_object_permissions(
            user, perm, obj.lendable_object
        ):
            return True
        return False
