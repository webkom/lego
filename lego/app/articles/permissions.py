from lego.permissions.keyword_permissions import KeywordPermissions
from lego.permissions.object_permissions import ObjectPermissions


class ArticlePermissions(KeywordPermissions, ObjectPermissions):
    perms_map = {
        'list': None,
        'retrieve': '/sudo/admin/articles/retrieve/',
        'create': '/sudo/admin/articles/create/',
        'update': '/sudo/admin/articles/update/',
        'partial_update': '/sudo/admin/articles/update/',
        'destroy': '/sudo/admin/articles/destroy/',
    }

    def has_object_permission(self, request, view, obj):
        return (KeywordPermissions.has_object_permission(self, request, view, obj) or
                ObjectPermissions.has_object_permission(self, request, view, obj))
