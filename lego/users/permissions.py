# -*- coding: utf8 -*-
from rest_framework import permissions

from lego.users.models import Membership


def can_retrieve_user(user, retriever):
    return user == retriever or retriever.has_perm('users.retrieve_user')


def can_retrieve_abakusgroup(group, retriever):
    return retriever.has_perm('users.retrieve_abakusgroup') or group in retriever.all_groups


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
    perms_map = {
        'PUT': 'users.change_abakusgroup',
        'PATCH': 'users.change_abakusgroup'
    }

    def check_model_perms(self, user, method):
        try:
            return user.has_perm(self.perms_map[method])
        except KeyError:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in ('PUT', 'PATCH'):
            user = request.user
            is_owner = bool(Membership.objects.filter(abakus_group=obj, user=user,
                                                      role=Membership.LEADER))

            return is_owner or self.check_model_perms(user, request.method)

        return True
