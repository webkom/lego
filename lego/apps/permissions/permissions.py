from prometheus_client import Summary
from rest_framework import permissions

from .models import ObjectPermissionsModel
from .registry import get_permission_string

permissions_has_permission = Summary('permissions_has_permission', 'Track has_permission')
permissions_has_object_permission = Summary(
    'permissions_has_object_permission', 'Track has_object_permission'
)


class AbakusPermission(permissions.BasePermission):

    OBJECT_METHODS = ['retrieve', 'update', 'partial_update', 'destroy']
    safe_actions = ['retrieve', 'metadata']

    default_permission = '/sudo/admin/{model_name}s/{action}/'
    default_require_auth = True

    permission_map = {}
    authentication_map = {}
    check_object_permission = False

    @classmethod
    def default_keyword_permission(cls, action, model_cls):
        """
        Create default permission string based on the model class, action and default_permission
        format. This is used when no permission is provided for a action in the permission_map.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name,
            'action': action
        }
        return cls.default_permission.format(**kwargs)

    def required_keyword_permissions(self, action, model_cls):
        """
        Get required keyword permissions based on the action and model class.
        Override the permission_map to create custom permissions, the default_keyword_permission
        function is used otherwise.
        """
        if action == 'partial_update':
            action = 'update'

        return self.permission_map.get(action, [
            self.default_keyword_permission(action, model_cls)
        ])

    def require_auth(self, action):
        """
        The first thing we need to check is if authentication is required. Override the
        authentication_map to change default behaviour. The default is provided by
        default_require_auth.
        """
        return self.authentication_map.get(
            action, self.default_require_auth
        )

    def is_authenticated(self, user):
        return user and user.is_authenticated()

    def _has_permission(self, action, model, user):
        requires_authentication = self.require_auth(action)

        if not requires_authentication:
            return True

        authenticated = self.is_authenticated(user)
        required_permissions = get_permission_string(model, action)

        # Check keyword permission (permission_map)
        has_perms = authenticated and user.has_perm(required_permissions)
        return has_perms

    def _has_object_permission(self, action, instance, user, safe_method=True):
        keyword_permissions = self._has_permission(action, instance, user)
        if keyword_permissions:
            return True

        # Check object permissions
        if isinstance(instance, ObjectPermissionsModel):
            if safe_method:
                return instance.can_view(user)
            return instance.can_edit(user)

        return False

    @permissions_has_permission.time()
    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        action = view.action
        user = request.user
        queryset = view.get_queryset()
        model = queryset.model

        has_permission = self._has_permission(action, model, user)
        setattr(request, 'user_has_keyword_permissions', has_permission)

        # If the queryset is based on the ObjectPermissionsModel model, return True and check
        # permissions in the filter backend and per object.
        object_permissions = issubclass(
            model, ObjectPermissionsModel
        ) or self.check_object_permission

        if object_permissions and not view.action == 'create':
            return True

        return has_permission

    @permissions_has_object_permission.time()
    def has_object_permission(self, request, view, obj):
        action = view.action
        user = request.user
        safe_method = action in self.safe_actions
        return self._has_object_permission(action, obj, user, safe_method)
