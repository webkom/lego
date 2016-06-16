from rest_framework import permissions

from .models import ObjectPermissionsModel


class AbakusObjectPermission(permissions.BasePermission):

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
        return [perm % kwargs for perm in perms] if perms else []

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        authenticated = request.user and request.user.is_authenticated()
        user = request.user

        required_permissions = self.get_required_object_permissions(
            self.perms_map.get(view.action),
            view.get_queryset().model
        )

        has_perms = authenticated and user.has_perms(required_permissions)
        setattr(request, 'user_has_keyword_permissions', has_perms)
        if has_perms:
            return True

        get_queryset = getattr(view, 'get_queryset', None)
        if get_queryset:
            object_permissions = issubclass(get_queryset().model, ObjectPermissionsModel)
            if object_permissions and not view.action == 'create':
                return True

        return False

    def has_object_permission(self, request, view, obj):
        authenticated = request.user and request.user.is_authenticated()
        user = request.user

        required_permissions = self.get_required_object_permissions(
            self.perms_map.get(view.action),
            view.get_queryset().model
        )

        if authenticated and user.has_perms(required_permissions):
            return True

        if isinstance(obj, ObjectPermissionsModel):
            if request.method in permissions.SAFE_METHODS:
                return obj.can_view(user)
            return obj.can_edit(user)

        return False


class AbakusAuthenticationPermission(permissions.BasePermission):

    OBJECT_METHODS = ['retrieve', 'update', 'partial_update', 'destroy']

    perms_map = {
        'list': True,
        'create': True,
        'retrieve': True,
        'update': True,
        'partial_update': True,
        'destroy': True,
    }

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not self.perms_map.get(view.action):
            return True

        authenticated = request.user and request.user.is_authenticated()

        get_queryset = getattr(view, 'get_queryset', None)
        if get_queryset and issubclass(get_queryset().model, ObjectPermissionsModel):
            return True

        return authenticated

    def has_object_permission(self, request, view, obj):
        authenticated = request.user and request.user.is_authenticated()

        if not self.perms_map.get(view.action):
            return True

        if isinstance(obj, ObjectPermissionsModel):
            if not obj.needs_auth():
                return True

        return authenticated
