from rest_framework import permissions

from .models import ObjectPermissionsModel


class AbakusPermission(permissions.BasePermission):

    OBJECT_METHODS = ['retrieve', 'update', 'partial_update', 'destroy']

    default_permission = '/sudo/admin/{model_name}s/{action}/'
    default_require_auth = True

    permission_map = {}
    authentication_map = {}

    def get_required_object_permissions(self, action, model_cls):
        if action == 'partial_update':
            action = 'update'

        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name,
            'action': action
        }
        perms = self.permission_map.get(action, [
            self.default_permission
        ])
        return [perm.format(**kwargs) for perm in perms]

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        required_permissions = self.get_required_object_permissions(
            view.action,
            view.get_queryset().model
        )

        requires_authentication = self.authentication_map.get(
            view.action, self.default_require_auth
        )

        authenticated = request.user and request.user.is_authenticated()
        user = request.user

        # Check explicit authentication requirements (authentication_map)
        if not requires_authentication:
            return True

        # Check keyword permission (permission_map)
        has_perms = authenticated and user.has_perms(required_permissions)
        setattr(request, 'user_has_keyword_permissions', has_perms)
        if has_perms:
            return True

        # If the queryset is based on the ObjectPermissionsModel model, return True and check
        # permissions in the filter backend and per object.
        get_queryset = getattr(view, 'get_queryset', None)
        if get_queryset:
            object_permissions = issubclass(get_queryset().model, ObjectPermissionsModel)
            if object_permissions and not view.action == 'create':
                return True

        return False

    def has_object_permission(self, request, view, obj):
        required_permissions = self.get_required_object_permissions(
            view.action,
            view.get_queryset().model
        )

        requires_authentication = self.authentication_map.get(
            view.action, self.default_require_auth
        )

        authenticated = request.user and request.user.is_authenticated()
        user = request.user

        # Check explicit authentication requirements (authentication_map)
        if not requires_authentication:
            return True

        # Check keyword permission (permission_map)
        if authenticated and user.has_perms(required_permissions):
            return True

        # If the object is based on the ObjectPermissionsModel, use object permissions.
        if isinstance(obj, ObjectPermissionsModel):
            if request.method in permissions.SAFE_METHODS:
                return obj.can_view(user)
            return obj.can_edit(user)

        return False
