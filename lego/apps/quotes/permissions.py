from lego.apps.permissions.permissions import AbakusPermission
from rest_framework.exceptions import PermissionDenied

from lego.apps.permissions.filters import AbakusObjectPermissionFilter


class QuotePermissionsFilter(AbakusObjectPermissionFilter):
    def filter_queryset(self, request, queryset, view):
        super(QuotePermissionsFilter, self).filter_queryset(request, queryset, view)
        has_approve_permission = request.user.has_perm('/sudo/admin/quotes/change-approval/')
        if 'approved' in request.query_params:
            approved = request.query_params['approved'].lower() == 'true'
            if approved:
                return queryset.filter(approved=True)
            else:
                if not has_approve_permission:
                    raise PermissionDenied
                else:
                    return queryset.filter(approved=False)
        elif has_approve_permission:
            return queryset
        else:
            return queryset.filter(approved=True)


class QuotePermissions(AbakusPermission):
    def has_object_permission(self, request, view, obj):
        obj = obj.quote
        return super().has_object_permission(request, view, obj)
