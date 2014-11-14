# -*- coding: utf8 -*-
from basis.models import BasisModel
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lego.users.models import User, AbakusGroup


class ObjectPermissionsModel(BasisModel):
    can_edit_users = models.ManyToManyField(User, related_name='can_edit_%(class)s')
    can_edit_groups = models.ManyToManyField(AbakusGroup,
                                             related_name='can_edit_%(class)s')

    can_view_groups = models.ManyToManyField(AbakusGroup,
                                             related_name='can_view_%(class)s')

    require_auth = models.BooleanField(_('require auth'), default=False)

    class Meta:
        abstract = True

    def can_view(self, user):
        return (user == self.created_by
                or len(set(user.all_groups).intersection(self.can_view_groups.all())) > 0)

    def can_edit(self, user):
        return (user == self.created_by
                or user in self.can_edit_users.all()
                or len(set(user.all_groups).intersection(self.can_edit_groups.all())))
