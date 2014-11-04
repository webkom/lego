# -*- coding: utf8 -*-
from django.contrib.auth.models import Group
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from basis.models import BasisModel


class AbakusGroup(BasisModel):
    name = models.CharField(_('name'), max_length=80, unique=True)
    description = models.CharField(_('description'), max_length=200, unique=True)
    parent = models.ForeignKey('self', blank=True, null=True, verbose_name=_('parent'))

    permission_groups = models.ManyToManyField(
        Group,
        verbose_name=_('permission groups'), blank=True,
        related_name='abakus_groups', related_query_name='abakus_groups'
    )

    class Meta:
        verbose_name = _('abakus group')
        verbose_name_plural = _('abakus groups')

    @cached_property
    def is_committee(self):
        if self.parent:
            return self.parent.name == 'Abakom'
        return False

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name,


class Membership(BasisModel):
    MEMBER = 'M'
    LEADER = 'L'
    CO_LEADER = 'CL'
    TREASURER = 'T'

    ROLES = (
        (MEMBER, _('Member')),
        (LEADER, _('Leader')),
        (CO_LEADER, _('Co-Leader')),
        (TREASURER, _('Treasurer'))
    )

    user = models.ForeignKey('users.User', verbose_name=_('user'))
    abakus_group = models.ForeignKey(AbakusGroup, verbose_name=_('abakus group'))
    role = models.CharField(_('role'), max_length=2, choices=ROLES, default=MEMBER)
    is_active = models.BooleanField(_('is active'), default=True)

    start_date = models.DateField(_('start date'), auto_now_add=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)

    class Meta:
        unique_together = ('user', 'abakus_group')

    def __str__(self):
        return '{0} is {1} in {2}'.format(self.user, self.get_role_display(), self.group)

