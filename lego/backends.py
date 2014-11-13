# -*- coding: utf8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission, Group


class AbakusModelBackend(ModelBackend):
    def get_group_permissions(self, user_obj, obj=None):
        """
        Returns a set of permission strings that this user has through his/her
        groups.
        """
        if user_obj.is_anonymous() or obj is not None:
            return set()
        if not hasattr(user_obj, '_group_perm_cache'):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                abakus_groups = [abakus_group.pk for abakus_group in user_obj.all_groups]
                permission_groups = Group.objects.filter(abakus_groups__in=abakus_groups).distinct()
                perms = Permission.objects.filter(group=permission_groups).distinct()

            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            user_obj._group_perm_cache = set("%s.%s" % (ct, name) for ct, name in perms)

        return user_obj._group_perm_cache

    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous() or obj is not None:
            return set()
        return self.get_group_permissions(user_obj, obj)
