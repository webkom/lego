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
        try:
            comment_target = GenericRelationField()\
                            .to_internal_value(request.data.get('comment_target'))
        except Exception:
            comment_target = None

        if comment_target:
            if not comment_target.can_view(request.user):
                raise ValidationError(
                    {'access_denied': 'You do not have permission to view the '
                                      'comment_target'})
