from rest_framework import permissions

from .models import ObjectPermissionsModel


class AbakusPermissions(permissions.BasePermission):

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

        # Check keyword permissions
        required_permission = self.get_required_object_permissions(
            self.perms_map.get(view.action),
            view.get_queryset().model
        )

        if required_permission is None \
                or (request.user.has_perms(required_permission) and user.is_authenticated()):
            setattr(request, 'user_has_keyword_permissions', user.is_authenticated() or
                    required_permission is None)
            return True

        # If we use object permission, this method needs to return True in order to run the
        # has_object_permission method.
        object_permissions = issubclass(view.get_queryset().model, ObjectPermissionsModel)
        if object_permissions and not view.action == 'create':
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Check keyword permissions
        required_permission = self.get_required_object_permissions(
            self.perms_map.get(view.action),
            view.get_queryset().model
        )
        if required_permission is None \
                or (request.user.has_perms(required_permission) and user.is_authenticated()):
            return True

        # Handle object permissions
        if isinstance(obj, ObjectPermissionsModel):
            if request.method in permissions.SAFE_METHODS:
                return obj.can_view(user)
            return obj.can_edit(user)

        return False
