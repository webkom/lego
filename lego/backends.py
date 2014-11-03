# -*- coding: utf8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


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
                user_groups_field = get_user_model()._meta.get_field('groups')
                user_groups_query = 'abakusgroup__%s' % user_groups_field.related_query_name()
                perms = Permission.objects.filter(**{user_groups_query: user_obj})
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            user_obj._group_perm_cache = set("%s.%s" % (ct, name) for ct, name in perms)
        return user_obj._group_perm_cache
