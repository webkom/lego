from rest_framework.permissions import BasePermission

from structlog import get_logger

from lego.apps.permissions.actions import action_to_permission
from lego.apps.permissions.api.permissions import LegoPermissions
from lego.apps.permissions.constants import CREATE, DELETE, EDIT, VIEW
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.permissions.utils import get_permission_handler

log = get_logger()


class EventPermissionHandler(PermissionHandler):

    perms_without_object = [CREATE, "administrate"]

    def event_type_keyword_permissions(self, event_type, perm):
        from lego.apps.events.models import Event

        return self.keyword_permission(Event, perm) + "{event_type}/".format(
            event_type=event_type
        )

    def has_event_type_level_permission(self, user, request, perm):
        if request is None:
            return True
        event_type = request.data.get("event_type")

        # The request might be a patch without the event_type. This should be allowed
        if event_type is None:
            return True

        required_keyword_permissions = self.event_type_keyword_permissions(
            event_type, perm
        )
        return user.has_perm(required_keyword_permissions)


class RegistrationPermissionHandler(PermissionHandler):

    allowed_individual = [VIEW, EDIT, DELETE]
    perms_without_object = [CREATE, "admin_register", "admin_unregister"]
    force_object_permission_check = True

    def is_self(self, perm, user, obj):
        if perm in self.allowed_individual:
            if obj is not None and obj.user == user:
                return True

        return False

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs,
    ):

        is_self = self.is_self(perm, user, obj)
        if is_self:
            return True

        return super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )


class EventTypePermission(LegoPermissions):
    def has_permission(self, request, view):
        from lego.apps.events.models import Event

        perm = action_to_permission(view.action)
        if perm in [CREATE, EDIT]:
            handler = get_permission_handler(Event)
            return handler.has_event_type_level_permission(request.user, request, perm)
        return super().has_permission(request, view)
