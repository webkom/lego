from rest_framework import permissions


class KeywordPermissions(permissions.BasePermission):
    _object_methods = ['retrieve', 'update', 'partial_update', 'destroy']
    perms_map = {
        'list': None,
        'create': None,
        'retrieve': None,
        'update': None,
        'partial_update': None,
        'destroy': None,
    }

    def has_permission(self, request, view):
        if view.action in self._object_methods:
            return True

        required_permission = self.perms_map.get(view.action)
        return required_permission is None or request.user.has_perm(required_permission)

    def has_object_permission(self, request, view, obj):
        required_permission = self.perms_map.get(view.action)
        return required_permission is None or request.user.has_perm(required_permission)
