from lego.apps.permissions.constants import CREATE, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from lego.utils.content_types import VALIDATION_EXCEPTIONS, string_to_instance


class ReactionTypePermissionHandler(PermissionHandler):

    default_keyword_permission = '/sudo/admin/reactions/{perm}'

    permission_map = {
        LIST: [],
        VIEW: [],
    }


class ReactionPermissionHandler(PermissionHandler):

    default_keyword_permission = '/sudo/admin/reactions/{perm}'
    force_object_permission_check = True

    def filter_queryset(self, user, queryset, **kwargs):
        if user.is_authenticated():
            return queryset.filter(created_by=user)
        return queryset

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):

        has_perm = super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)

        if has_perm:
            return True

        if user.is_authenticated():

            if perm == LIST:
                # The filter removes unwanted objects.
                return True

            if perm == CREATE:
                """
                We need to validate the data tries to create. We have to do this manually because
                this happens before rest_framework parses the request.
                """
                request = kwargs.get('request')
                if not request:
                    return False
                return self.check_target_permission(user, request)

            elif obj is not None:
                return obj.created_by == user

        return False

    def check_target_permission(self, user, request):
        try:
            target = request.data.get('target', None)
            if target:
                obj = string_to_instance(target)
                return user.has_perm(VIEW, obj)
        except VALIDATION_EXCEPTIONS:
            pass

        return False
