from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.permissions import AbakusPermission
from rest_framework.fields import Field


class AbakusPermissionField(Field):
    def __init__(self):
        super().__init__(read_only=True)

    def get_attribute(self, obj):
        return obj

    def __parse_permission_string(self, obj, action):
        kwargs = {
            'app_label': obj._meta.app_label,
            'model_name': obj._meta.model_name,
            'action': action
        }
        return AbakusPermission.default_permission.format(**kwargs)

    def to_representation(self, obj):
        permissions = []
        
        view = self.context['view']
        user = self.context['request'].user

        # Check if the object is using the object permissions model
        if isinstance(obj, ObjectPermissionsModel):
            # Can the user edit the object?
            if obj.can_edit(user):
                permissions.append('edit')
        else:
            # The object is not using the object permissions model, check keyword permissions instead
            if user.has_perm(self.__parse_permission_string(obj, 'update')):
                permissions.append('edit')

        # Check if user has permissions to destroy the object
        if user.has_perm(self.__parse_permission_string(obj, 'destroy')):
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
