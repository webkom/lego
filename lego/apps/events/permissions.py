from structlog import get_logger

from lego.apps.permissions.permissions import AbakusPermission

log = get_logger()


class NestedEventPermissions(AbakusPermission):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)
