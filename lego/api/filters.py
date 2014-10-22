# -*- coding: utf8 -*-
from rest_framework import filters


class RequireAuthFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not request.user.is_authenticated():
            return queryset.filter(require_auth=False)
        return queryset
