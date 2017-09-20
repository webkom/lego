from django.contrib.auth.backends import ModelBackend
from django.db import models

from lego.apps.permissions.keyword import KeywordPermissions
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.stats.statsd_client import statsd


class LegoPermissionBackend(ModelBackend):
    """
    Check permissions on a object using the builtin django user.has_perms() function.
    """

    def _get_permissions(self, user_obj, obj, from_name):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        return set()

    def has_module_perms(self, user_obj, app_label):
        return False

    @statsd.timer('permission.has_perm')
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False

        if obj is None:
            # Take a shortcut and check KeywordPermissions only if no object are defined.
            return KeywordPermissions.has_perm(user_obj, perm)

        if isinstance(obj, models.Model):
            permission_handler = get_permission_handler(obj)
            return permission_handler.has_perm(user_obj, perm, obj=obj)
        elif isinstance(obj, models.QuerySet):
            permission_handler = get_permission_handler(obj.model)
            return permission_handler.has_perm(user_obj, perm, queryset=obj)
        elif issubclass(obj, models.Model):
            permission_handler = get_permission_handler(obj)
            return permission_handler.has_perm(user_obj, perm, queryset=obj.objects.none())

        return False
