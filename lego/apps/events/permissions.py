from structlog import get_logger

from lego.apps.permissions.constants import CREATE, DELETE, EDIT, LIST, VIEW
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.permissions import PermissionHandler

log = get_logger()


class EventPermissionHandler(PermissionHandler):

    perms_without_object = [CREATE, 'administrate']
    authentication_map = {VIEW: False, LIST: False}
    force_queryset_filtering = True

    def filter_queryset(self, user, queryset, **kwargs):
        if not user.is_authenticated or not user.is_abakom_member:
            return queryset.filter(is_abakom_only=False)
        return queryset

    def has_perm(
        self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        """
        Check permission on a object.
        """
        if obj is None and queryset is None:
            raise ValueError('You have to at least provide one parameter, obj or queryset.')
        elif self.force_object_permission_check and self.skip_object_permission:
            raise ValueError('You cannot force and skip the permission checks at the same time!')

        require_auth = self.require_auth(perm, obj)
        authenticated = self.is_authenticated(user)

        if require_auth and not authenticated:
            return False

        if obj is not None:
            model = obj.__class__
        else:
            model = queryset.model
        if model is None:
            raise ValueError('The model is null, cannot continue.')

        if perm in self.safe_methods:
            if obj:
                created_by = self.created_by(user, obj)
                if created_by:
                    return True

                if isinstance(obj, ObjectPermissionsModel) and obj.is_abakom_only:
                    return authenticated and user.is_abakom_member

                return True

        if check_keyword_permissions:
            required_keyword_permissions = self.required_keyword_permissions(model, perm)
            has_perms = user.has_perms(required_keyword_permissions)
            if has_perms:
                return True

        return False


class RegistrationPermissionHandler(PermissionHandler):

    allowed_individual = [VIEW, EDIT, DELETE]
    perms_without_object = [CREATE, 'admin_register', 'admin_unregister']
    force_object_permission_check = True

    def is_self(self, perm, user, obj):
        if perm in self.allowed_individual:
            if obj is not None and obj.user == user:
                return True

        return False

    def has_perm(
        self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):

        is_self = self.is_self(perm, user, obj)
        if is_self:
            return True

        return super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)
