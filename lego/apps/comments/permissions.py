from rest_framework.exceptions import ValidationError

from lego.apps.permissions.permissions import AbakusPermission
from lego.utils.serializers import GenericRelationField


class CommentPermission(AbakusPermission):

    def has_permission(self, request, view):

        has_permission = super(CommentPermission, self).has_permission(request, view)

        if not has_permission:
            return False

        if view.action == 'create':
            self.check_target_permissions(request)

        return True

    def check_target_permissions(self, request):
        comment_target = None
        try:
            comment_target = GenericRelationField()\
                            .to_internal_value(request.data.get('comment_target'))
        except ValidationError as e:
            # Comment_target was not found. This will be raised in serializer at a later point.
            # Validation does not belong in permissions
            pass

        if comment_target:
            if not comment_target.can_view(request.user):
                return False
