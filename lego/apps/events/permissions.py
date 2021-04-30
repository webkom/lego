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
        """
        Get the keyword permission string required for a permission for a specific event type

        :return: The keyword permission the user needs
        """
        from lego.apps.events.models import Event

        return self.keyword_permission(Event, perm) + "{event_type}/".format(
            event_type=event_type
        )

    def has_event_type_level_permission(self, user, request, perm):
        """
        Check if a user has the required event_type
        permissions for a certain action.

        **WARNING**: This method ONLY enforces keyword permissions for event types. It does not
        check object permissions for the event and shoud not be used on it's own to check
        permissions on an object.

        Return `True` if the user has permission to perform the request with the specified
        event_type
        """

        if request is None:
            return False

        event_type = request.data.get("event_type")

        # The request might be a patch without the event_type. This should be allowed
        if perm is EDIT and event_type is None:
            return True

        # This only makes sense to use for EDIT and CREATE. And to simplify the permissions, we only
        # check the CREATE permission for both.
        required_keyword_permissions = self.event_type_keyword_permissions(
            event_type, CREATE
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

        handler = get_permission_handler(Event)
        perm = action_to_permission(view.action)

        # Only check keyword permissions for CREATE
        if perm is CREATE:
            return handler.has_event_type_level_permission(request.user, request, perm)
        # The user needs to have permission to edit the event_type AND needs to pass the
        # main permission check
        if perm is EDIT:
            if not handler.has_event_type_level_permission(request.user, request, perm):
                return False

        return super().has_permission(request, view)
