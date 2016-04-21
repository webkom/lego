from django.db.models import Q
from rest_framework import filters

from lego.permissions.models import ObjectPermissionsModel


class AbakusObjectPermissionFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        if issubclass(queryset.model, ObjectPermissionsModel) and not\
                getattr(request, 'user_has_keyword_permissions', False):
            if not request.user.is_authenticated():
                return queryset.filter(require_auth=False, can_view_groups=None)

            groups = [abakus_group.pk for abakus_group in request.user.all_groups]
            return queryset.filter(
                Q(can_view_groups=None) | Q(can_view_groups__in=groups) | Q(created_by=request.user)
            ).distinct()

        return queryset
