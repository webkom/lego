from rest_framework import permissions


class ObjectPermissions(permissions.BasePermission):
    """
    A permission class for use in DRF-views that want to utilize object permissions.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return obj.can_view(user)

        return obj.can_edit(user)
