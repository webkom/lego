from django.contrib.auth.backends import ModelBackend

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.registry import parse_permission_string


class AbakusPermissionBackend:
    """
    This backend makes it possible to check for keyword permissions using the standard django
    method: user.has_perm('/sudo/').
    """

    authenticate = ModelBackend.authenticate
    get_user = ModelBackend.get_user
    user_can_authenticate = ModelBackend.user_can_authenticate

    def get_group_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous or obj is not None:
            return set()

        perms = set()
        for group in user_obj.all_groups:
            available_perms = group.permissions
            if available_perms:
                perms.update(available_perms)
        return perms

    def get_all_permissions(self, user_obj, obj=None):
        return self.get_group_permissions(user_obj, obj)

    def has_perm(self, user_obj, perm, obj=None):
        perm_tuple = parse_permission_string(perm)
        if perm_tuple:
            keyword_perms, object_perm = perm_tuple
            perms = self.get_all_permissions(user_obj)
            has_keyword_permission = True
            for keyword_perm in keyword_perms:
                if not self.has_keyword_perm(keyword_perm, perms):
                    has_keyword_permission = False
            if has_keyword_permission:
                return True

            if obj and isinstance(obj, ObjectPermissionsModel):
                if object_perm == 'can_view':
                    return obj.can_view(user_obj)
                elif object_perm == 'can_edit':
                    return obj.can_edit(user_obj)
        return False

    def has_keyword_perm(self, keyword_perm, perms):
        for own_perm in perms:
            if keyword_perm.startswith(own_perm):
                return True
        return False
