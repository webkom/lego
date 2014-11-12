# -*- coding: utf8 -*-
from django.db import models
from lego.users.models import User, AbakusGroup


class ObjectPermissionsMixin(models.Model):
    can_edit_users = models.ManyToManyField(User, related_name='can_edit_%(class)s')
    can_edit_groups = models.ManyToManyField(AbakusGroup,
                                             related_name='can_edit_%(class)s')

    can_view_groups = models.ManyToManyField(AbakusGroup,
                                             related_name='can_view_%(class)s')

    class Meta:
        abstract = True

    def can_view(self, user):
        return len(set(user.groups).intersection(self.can_edit_groups))

    def can_edit(self, user):
        if user in self.can_edit_users or len(set(user.groups).intersection(self.can_edit_groups)):
            return True
