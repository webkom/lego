from structlog import get_logger

from lego.apps.permissions.constants import CREATE, DELETE, EDIT, LIST, VIEW
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.permissions import PermissionHandler

log = get_logger()


class EventPermissionHandler(PermissionHandler):

    perms_without_object = [CREATE, 'administrate']
    authentication_map = {VIEW: False, LIST: False}
    force_queryset_filtering = True

    def filter_queryset(self, user, queryset, **kwargs):
        if not user.is_authenticated or not user.is_abakom_member:
            return queryset.filter(is_abakom_only=False)
        return queryset

    def has_perm(
        self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        if perm == LIST or (perm == VIEW and not obj):
            return False
        return super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)


class RegistrationPermissionHandler(PermissionHandler):

    allowed_individual = [VIEW, EDIT, DELETE]
    perms_without_object = [CREATE, 'admin_register', 'admin_unregister']
    force_object_permission_check = True

    def is_self(self, perm, user, obj):
        if perm in self.allowed_individual:
            if obj is not None and obj.user == user:
                return True

        return False

    def has_perm(
        self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):

        is_self = self.is_self(perm, user, obj)
        if is_self:
            return True

        return super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)
