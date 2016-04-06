from rest_framework.exceptions import PermissionDenied

from lego.permissions.filters import ObjectPermissionsFilter
from lego.permissions.keyword_permissions import KeywordPermissions
from lego.permissions.object_permissions import ObjectPermissions


class QuotePermissionsFilter(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        super(QuotePermissionsFilter, self).filter_queryset(request, queryset, view)
        has_approve_permission = request.user.has_perm(QuotePermissions.perms_map['approve'])
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


class QuotePermissions(KeywordPermissions, ObjectPermissions):
    perms_map = {
        'list': None,
        'list-approved': '/sudo/admin/quotes/list-approved/',
        'like': None,
        'approve': '/sudo/admin/quotes/change-approval/',
        'unapprove': '/sudo/admin/quotes/change-approval/',
        'retrieve': '/sudo/admin/quotes/retrieve/',
        'create': '/sudo/admin/quotes/create/',
        'update': '/sudo/admin/quotes/update/',
        'partial_update': '/sudo/admin/quotes/update/',
        'destroy': '/sudo/admin/quotes/destroy/',
    }

    def has_object_permission(self, request, view, obj):
        return (KeywordPermissions.has_object_permission(self, request, view, obj) or
                ObjectPermissions.has_object_permission(self, request, view, obj))
