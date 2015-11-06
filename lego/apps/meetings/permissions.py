from lego.permissions.keyword_permissions import KeywordPermissions
from lego.permissions.object_permissions import ObjectPermissions


class MeetingPermissions(KeywordPermissions, ObjectPermissions):
    perms_map = {
        'list': None,
        'retrieve': '/sudo/admin/meetings/retrieve/',
        'create': '/sudo/admin/meetings/create/',
        'update': '/sudo/admin/meetings/update/',
        'partial_update': '/sudo/admin/meetings/update/',
        'destroy': '/sudo/admin/meetings/destroy/',
    }

    def has_object_permission(self, request, view, obj):
        return (KeywordPermissions.has_object_permission(self, request, view, obj) or
                ObjectPermissions.has_object_permission(self, request, view, obj))
