from rest_framework import permissions

from lego.apps.permissions.actions import action_to_permission
from lego.apps.permissions.utils import get_permission_handler


class LegoPermissions(permissions.BasePermission):
    """
    Check permissions on API requests.
    """

    def permission_handler(self, view):
        handler = getattr(
            view, 'permission_handler', None
        )
        if not handler:
            handler = get_permission_handler(view.get_queryset().model)

        return handler

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        permission = action_to_permission(view.action)
        if permission is None:
            return False

        user = request.user
        queryset = view.get_queryset()
        permission_handler = self.permission_handler(view)

        has_perm = permission_handler.has_perm(
            user, permission, queryset=queryset, view=view, request=request
        )
        setattr(request, 'user_has_perm', has_perm)

        if has_perm:
            return True

        object_permissions = permission_handler.has_object_level_permissions(
            user, permission, queryset=queryset
        )

        if object_permissions:
            return True

        return has_perm

    def has_object_permission(self, request, view, obj):
        if getattr(request, 'user_has_perm', False):
            return True

        permission = action_to_permission(view.action)
        user = request.user
        queryset = view.get_queryset()
        permission_handler = self.permission_handler(view)

        return permission_handler.has_perm(
            user, permission, queryset=queryset, obj=obj, check_keyword_permissions=False
        )
