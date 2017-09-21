from rest_framework import filters

from lego.apps.permissions.utils import get_permission_handler
from lego.apps.stats.statsd_client import statsd


class LegoPermissionFilter(filters.BaseFilterBackend):
    """
    Use permissions to filter API responses.
    """

    def permission_handler(self, view, queryset):
        handler = getattr(
            view, 'permission_handler', None
        )
        if not handler:
            handler = get_permission_handler(queryset.model)

        return handler

    @statsd.timer('permissions.api_filter_queryset')
    def filter_queryset(self, request, queryset, view):

        has_keyword_permissions = getattr(request, 'user_has_perm', False)
        if has_keyword_permissions:
            return queryset

        if not request:
            return queryset

        permission_handler = self.permission_handler(view, queryset)

        return permission_handler.filter_queryset(request.user, queryset, view=view)
