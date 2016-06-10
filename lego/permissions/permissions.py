from rest_framework import permissions

from .models import ObjectPermissionsModel


class AbakusPermissions(permissions.BasePermission):
    """
    This class handles all permissions in the api. Permissions is defined using the perms_map.
    You can override tis class and use it in viewsets. (permission_classes=[NewAbakusPermissions])

    1. If the value associated with an action is falsy (False, None, []) no authentication is
    required.

    2. If the value is True and only True, authentication is required, but that's all.

    3. If the value is a list of strings, the string represents a required keyword permission. If
    the list contains multiple elements, the OR operator will be used.
    """

    OBJECT_METHODS = ['retrieve', 'update', 'partial_update', 'destroy']

    perms_map = {
        'list': ['/sudo/admin/%(model_name)ss/list/'],
        'create': ['/sudo/admin/%(model_name)ss/create/'],
        'retrieve': ['/sudo/admin/%(model_name)ss/retrieve/'],
        'update': ['/sudo/admin/%(model_name)ss/update/'],
        'partial_update': ['/sudo/admin/%(model_name)ss/update/'],
        'destroy': ['/sudo/admin/%(model_name)ss/destroy/'],
    }

    def get_required_object_permissions(self, perms, model_cls):
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        return [perm % kwargs for perm in perms] if perms else perms

    def has_permission(self, request, view):
        user = request.user
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        # Check keyword permissions.
        required_permissions = self.get_required_object_permissions(
            self.perms_map.get(view.action),
            view.get_queryset().model
        )

        # Case 1 - The required permission is falsy, grant access.
        if not bool(required_permissions):
            user_has_keyword_permissions = True
        # Case 2 - The required permission is True.
        elif isinstance(required_permissions, bool) and required_permissions:
            user_has_keyword_permissions = user.is_authenticated()
        # Case 3 - Check if the user is logged inn and has keyword permission.
        else:
            has_perms = user.is_authenticated() and request.user.has_perms(required_permissions)
            user_has_keyword_permissions = has_perms

        setattr(request, 'user_has_keyword_permissions', user_has_keyword_permissions)
        if user_has_keyword_permissions:
            return True

        # If we use object permission, this method needs to return True in order to run the
        # has_object_permission method. The create action is excluded, the create action requires
        # keyword permissions.
        object_permissions = issubclass(view.get_queryset().model, ObjectPermissionsModel)
        if object_permissions and not view.action == 'create':
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Check keyword permissions
        required_permissions = self.get_required_object_permissions(
            self.perms_map.get(view.action),
            view.get_queryset().model
        )
        if not bool(required_permissions):
            return True
        elif isinstance(required_permissions, bool) and required_permissions:
            return True
        elif user.is_authenticated() and request.user.has_perms(required_permissions):
            return True

        # Handle object permissions
        if isinstance(obj, ObjectPermissionsModel):
            if request.method in permissions.SAFE_METHODS:
                return obj.can_view(user)
            return obj.can_edit(user)

        return False
