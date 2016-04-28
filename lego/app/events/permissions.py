from lego.permissions.keyword_permissions import KeywordPermissions
from lego.permissions.object_permissions import ObjectPermissions


class EventPermissions(KeywordPermissions, ObjectPermissions):
    perms_map = {
        'list': None,
        'retrieve': '/sudo/admin/events/retrieve/',
        'create': '/sudo/admin/events/create/',
        'update': '/sudo/admin/events/update/',
        'partial_update': '/sudo/admin/events/update/',
        'destroy': '/sudo/admin/events/destroy/',
    }

    def has_object_permission(self, request, view, obj):
        return (KeywordPermissions.has_object_permission(self, request, view, obj) or
                ObjectPermissions.has_object_permission(self, request, view, obj))


class NestedEventPermissions(EventPermissions):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)
