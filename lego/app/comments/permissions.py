from lego.permissions.keyword_permissions import KeywordPermissions
from lego.permissions.object_permissions import ObjectPermissions


class CommentPermissions(KeywordPermissions, ObjectPermissions):
    perms_map = {
        # create permission is enforced in serializer
        'create': None,
        'update': '/sudo/admin/comments/update/',
        'partial_update': '/sudo/admin/comments/update/',
        'destroy': '/sudo/admin/comments/destroy/',
    }

    def has_object_permission(self, request, view, obj):
        return (KeywordPermissions.has_object_permission(self, request, view, obj.content_object) or
                ObjectPermissions.has_object_permission(self, request, view, obj))
