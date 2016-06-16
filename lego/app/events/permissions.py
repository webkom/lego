from lego.permissions.permissions import AbakusObjectPermission


class EventPermissions(AbakusObjectPermission):
    # This mapping is needed to enforce events permissions on nested objects.
    perms_map = {
        'list': ['/sudo/admin/events/list/'],
        'create': ['/sudo/admin/events/create/'],
        'retrieve': ['/sudo/admin/events/retrieve/'],
        'update': ['/sudo/admin/events/update/'],
        'partial_update': ['/sudo/admin/events/update/'],
        'destroy': ['/sudo/admin/events/destroy/'],
    }


class NestedEventPermissions(EventPermissions):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)
