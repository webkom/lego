from lego.apps.permissions.constants import EDIT
from lego.apps.permissions.permissions import PermissionHandler


class QuotePermissionHandler(PermissionHandler):

    permission_map = {
        'random': [],
        'approve': ['/sudo/admin/quotes/change-approval/'],
        'unapprove': ['/sudo/admin/quotes/change-approval/'],
    }

    def filter_queryset(self, user, queryset, **kwargs):
        queryset = super().filter_queryset(user, queryset)
        access_unapproved = user.has_perm(EDIT, queryset)

        if not access_unapproved:
            return queryset.filter(approved=True)
        return queryset
