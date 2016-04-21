from lego.permissions.permissions import AbakusPermissions


class EventPermissions(AbakusPermissions):
    perms_map = {
        'list': None,
        'retrieve': '/sudo/admin/events/retrieve/',
        'create': '/sudo/admin/events/create/',
        'update': '/sudo/admin/events/update/',
        'partial_update': '/sudo/admin/events/update/',
        'destroy': '/sudo/admin/events/destroy/',
    }


class NestedEventPermissions(EventPermissions):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)
