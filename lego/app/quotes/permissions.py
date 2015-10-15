# -*- coding: utf8 -*-
from lego.permissions.keyword_permissions import KeywordPermissions
from lego.permissions.object_permissions import ObjectPermissions


class QuotePermissions(KeywordPermissions, ObjectPermissions):
    perms_map = {
        'list': None,
        'list-approved': '/sudo/admin/quotes/list-approved/',
        'unlike': '/sudo/admin/quotes/unlike/',
        'like': '/sudo/admin/quotes/like/',
        'retrieve': '/sudo/admin/quotes/retrieve/',
        'create': '/sudo/admin/quotes/create/',
        'update': '/sudo/admin/quotes/update/',
        'partial_update': '/sudo/admin/quotes/update/',
        'destroy': '/sudo/admin/quotes/destroy/',
    }

    def has_object_permission(self, request, view, obj):
        return (KeywordPermissions.has_object_permission(self, request, view, obj) or
                ObjectPermissions.has_object_permission(self, request, view, obj))
