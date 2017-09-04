from structlog import get_logger

from lego.apps.permissions.constants import CREATE, DELETE, EDIT, VIEW
from lego.apps.permissions.permissions import PermissionHandler

log = get_logger()


class EventPermissionHandler(PermissionHandler):

    perms_without_object = [CREATE, 'administrate']


class RegistrationPermissionHandler(PermissionHandler):

    allowed_individual = [VIEW, EDIT, DELETE]
    perms_without_object = [CREATE, 'admin_register']
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
