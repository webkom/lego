from lego.apps.permissions.permissions import AbakusPermission


class EventPermissions(AbakusPermission):
    permission_map = {
        'admin_register': ['/sudo/admin/events/create/'],  # what permission to use??
    }


class NestedEventPermissions(AbakusPermission):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)
