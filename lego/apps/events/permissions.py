from lego.apps.permissions.permissions import AbakusPermission


class EventPermissions(AbakusPermission):
    permission_map = {
        'create': ['/sudo/admin/events/create/','/sudo/admin/events/admin-create/'],
    }


class NestedEventPermissions(AbakusPermission):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)
