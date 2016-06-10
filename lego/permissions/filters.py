from django.db.models import Q
from rest_framework import filters

from lego.permissions.models import ObjectPermissionsModel


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

        # If the queryset consists og object permissions, filter based on authentication status
        # and group membership.
        if issubclass(queryset.model, ObjectPermissionsModel):

            # Unauthenticated users can only see objects with no auth required.
            if not request.user.is_authenticated():
                return queryset.filter(require_auth=False, can_view_groups=None)

            # User is authenticated, display objects created by user or object with group rights.
            groups = [abakus_group.pk for abakus_group in request.user.all_groups]
            return queryset.filter(
                Q(can_view_groups=None) | Q(can_view_groups__in=groups) | Q(created_by=request.user)
            ).distinct()

        return queryset
