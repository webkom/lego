from django.db.models import Q
from prometheus_client import Summary
from rest_framework import filters

from lego.apps.permissions.models import ObjectPermissionsModel

permissions_filter = Summary('permissions_filter', 'Track permission filter')


@permissions_filter.time()
def filter_queryset(user, queryset):
    # If the queryset consists og object permissions, filter based on authentication status
    # and group membership.
    if issubclass(queryset.model, ObjectPermissionsModel):

        # Unauthenticated users can only see objects with no auth required.
        if not user.is_authenticated():
            return queryset.filter(require_auth=False, can_view_groups=None)

        # User is authenticated, display objects created by user or object with group rights.
        groups = [abakus_group.pk for abakus_group in user.all_groups]
        return queryset.filter(
            Q(can_view_groups=None) | Q(can_view_groups__in=groups) | Q(created_by=user)
        ).distinct()

    return queryset


class AbakusObjectPermissionFilter(filters.BaseFilterBackend):
    """
    Custom filter class. This filter uses request.user_has_keyword_permissions to determine
    keyword permissions, object permissions gets filtered here.
    """
    def filter_queryset(self, request, queryset, view):
        # If user has keyword permissions, return entire queryset.
        has_keyword_permissions = getattr(request, 'user_has_keyword_permissions', False)
        if has_keyword_permissions:
            return queryset

        return filter_queryset(request.user, queryset)
