from django.db.models import Q
from rest_framework import filters


class ObjectPermissionsFilter(filters.BaseFilterBackend):
    """
    A filter backend for DRF-views that want to be able to filter based on object permissions.
    """
    def filter_queryset(self, request, queryset, view):
        if not request.user.is_authenticated():
            return queryset.filter(require_auth=False, can_view_groups=None)

        groups = [abakus_group.pk for abakus_group in request.user.all_groups]
        return queryset.filter(
            Q(can_view_groups=None) | Q(can_view_groups__in=groups) | Q(created_by=request.user)
        )
