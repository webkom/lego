# -*- coding: utf8 -*-
from lego.users.models import AbakusGroup
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import BaseFilterBackend


class AbakusGroupFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user

        if not user.is_authenticated():
            return PermissionDenied()

        if user.has_perm('users.list_abakusgroup'):
            return AbakusGroup.objects.all()

        return AbakusGroup.objects.filter(membership__user=user)
