from lego.permissions.keyword_permissions import KeywordPermissions
from lego.permissions.object_permissions import ObjectPermissions


class FlatpagePermissions(KeywordPermissions, ObjectPermissions):
    perms_map = {
        'list': None,
        'retrieve': '/sudo/admin/flatpages/retrieve/',
        'create': '/sudo/admin/flatpages/create/',
        'update': '/sudo/admin/flatpages/update/',
        'partial_update': '/sudo/admin/flatpages/update/',
        'destroy': '/sudo/admin/flatpages/destroy/',
    }

    def has_object_permission(self, request, view, obj):
        return (KeywordPermissions.has_object_permission(self, request, view, obj) or
                ObjectPermissions.has_object_permission(self, request, view, obj))
