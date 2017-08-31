from lego.apps.permissions.constants import CREATE, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from lego.utils.content_types import VALIDATION_EXCEPTIONS, string_to_instance


class CommentPermissionHandler(PermissionHandler):

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):

        can_access_target = False
        if user.is_authenticated() and perm == CREATE:
            """
            We need to validate the data tries to create. We have to do this manually because
            this happens before rest_framework parses the request.
            """
            request = kwargs.get('request')
            if request:
                can_access_target = self.check_target_permission(user, request)

        has_perm = super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)

        if has_perm:
            if perm == CREATE:
                return can_access_target

        return has_perm

    def check_target_permission(self, user, request):
        try:
            target = request.data.get('comment_target', None)
            if target:
                obj = string_to_instance(target)
                return user.has_perm(VIEW, obj)
        except VALIDATION_EXCEPTIONS:
            pass

        return False
