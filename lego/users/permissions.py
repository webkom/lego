# -*- coding: utf8 -*-
from rest_framework import permissions

from lego.users.models import Membership


def can_retrieve_user(user, retriever):
    return user == retriever or retriever.has_perm('users.retrieve_user')


def can_view_abakusgroup(group, user):
    return user.has_perm('users.retrieve_abakusgroup') or group in user.all_groups


class UsersObjectPermissions(permissions.BasePermission):
    perms_map = {
        'PUT': 'users.change_user',
        'PATCH': 'users.change_user'
    }

    def check_model_perms(self, user, method):
        try:
            return user.has_perm(self.perms_map[method])
        except KeyError:
            return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user == obj:
            return True

        return self.check_model_perms(request.user, request.method)

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.has_perm('users.list_user')

        return True


class AbakusGroupObjectPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('PUT', 'PATCH'):
            is_owner = bool(Membership.objects.filter(abakus_group=obj, role=Membership.LEADER))
            return is_owner or request.user.has_perm('users.change_abakusgroup')

        return True
