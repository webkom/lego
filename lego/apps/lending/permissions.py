from lego.apps.permissions.constants import CREATE, DELETE, EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from django.db.models import Q


class LendingInstancePermissionHandler(PermissionHandler):
    force_object_permission_check = True
    authentication_map = {LIST: False, VIEW: False}
    default_require_auth = True

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        if perm == LIST:
            return True
        if not user.is_authenticated:
            return False

        # Check object permissions before keywork perms
        if obj is not None:
            if self.has_object_permissions(user, perm, obj):
                return True

            if perm == EDIT and self.created_by(user, obj):
                return True

        if perm == CREATE:
            return True

        has_perm = super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )

        if has_perm:
            return True

        return False

    def has_object_permissions(self, user, perm, obj):
        if perm == DELETE:
            return False
        if perm == EDIT and obj.created_by == user:
            return True
        if perm == CREATE:
            return True
        return not (perm == DELETE or perm == EDIT)

    def filter_queryset(self, user, queryset, **kwargs):
        if user.is_authenticated:
            return queryset.filter(
                Q(created_by=user) |
                Q(lendable_object__responsible_groups__in=user.abakus_groups)
            ).distinct()
        return queryset.none()
