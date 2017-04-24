from rest_framework import exceptions

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.permissions import AbakusPermission
from lego.utils.content_types import VALIDATION_EXCEPTIONS, string_to_instance


class CommentPermission(AbakusPermission):

    def has_permission(self, request, view):

        has_permission = super().has_permission(request, view)

        if not has_permission:
            return False

        if view.action == 'create':
            return self.check_target_permissions(request)

        return True

    def check_target_permissions(self, request):
        comment_target = request.data.get('comment_target')

        if not comment_target:
            raise exceptions.ValidationError('comment_target are invalid')

        try:
            instance = string_to_instance(comment_target)
            # We only support permissions checks on ObjectPermissionsModels at this time!
            # We allow comments creation on other models because we don't have any way to verify it.
            if isinstance(instance, ObjectPermissionsModel):
                return instance.can_view(request.user)
            else:
                return True
        except VALIDATION_EXCEPTIONS:
            pass

        raise exceptions.ValidationError('comment_target could not be verified')
