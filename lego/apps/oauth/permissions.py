from lego.apps.permissions.constants import LIST
from lego.apps.permissions.permissions import PermissionHandler


class APIApplicationPermissionHandler(PermissionHandler):

    permission_map = {
        LIST: [],
    }

    def filter_queryset(self, user, queryset, **kwargs):
        if user.is_authenticated:
            return queryset.filter(user=user)
        return queryset.none()
