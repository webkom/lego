from lego.apps.permissions.permissions import PermissionHandler


class APIApplicationPermissionHandler(PermissionHandler):

    force_queryset_filtering = True

    def filter_queryset(self, user, queryset, **kwargs):
        if user.is_authenticated:
            return queryset.filter(user=user)
        return queryset.none()
