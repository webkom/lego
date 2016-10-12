from django.contrib.auth.backends import ModelBackend

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.permissions import AbakusPermission


class AbakusPermissionBackend:
    """
    This backend makes it possuble to check for keyword permissions using the standard django
    method: user.has_perm('/sudo/').
    """

    authenticate = ModelBackend.authenticate
    get_user = ModelBackend.get_user
    user_can_authenticate = ModelBackend.user_can_authenticate

    def get_group_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous() or obj is not None:
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
        perms = self.get_all_permissions(user_obj, obj)
        for own_perm in perms:
            if perm.startswith(own_perm):
                return True

        return False


class AbakusViewSetPermission:
    """
    This class makes it possible to append a users permissions to a viewset response
    """
    @classmethod
    def __parse_permission_string(cls, obj, action):
        kwargs = {
            'app_label': obj._meta.app_label,
            'model_name': obj._meta.model_name,
            'action': action
        }
        return AbakusPermission.default_permission.format(**kwargs)

    @staticmethod
    def get_permissions(view, obj, user):
        permissions = []

        # Return permissions regarding if the user can create objects
        if view.action == 'list':
            # Check if user has permissions to create an object in this model
            if user.has_perm(AbakusViewSetPermission.__parse_permission_string(obj, 'create')):
                permissions.append('create')
        elif view.action == 'retrieve':
            # Check if the object is using the object permissions model
            if isinstance(obj, ObjectPermissionsModel):
                # Can the user edit the object?
                if obj.can_edit(user):
                    permissions.append('edit')
            else:
                # The object is not using the object permissions model,
                # check keyword permissions instead
                if user.has_perm(AbakusViewSetPermission.__parse_permission_string(obj, 'update')):
                    permissions.append('edit')

            # Check if user has permissions to destroy the object
            if user.has_perm(AbakusViewSetPermission.__parse_permission_string(obj, 'destroy')):
                permissions.append('delete')

            # Loop through all the permission classes in the ViewSet
            permission_classes = view.get_permissions()
            for permission_class in permission_classes:
                # Loop through all the actions and their permission string for the permission class
                if 'permission_map' in dir(permission_class):
                    for action, permission_string in permission_class.permission_map.items():
                        if action not in AbakusPermission.OBJECT_METHODS:
                            # Check if the user has the required permission for that action
                            if user.has_perm(permission_string[0]):
                                permissions.append(action)

        # Return the permission list
        return permissions
