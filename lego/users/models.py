# -*- coding: utf8 -*-
from basis.models import BasisModel, PersistentModel

from django.contrib import auth
from django.contrib.auth.models import AbstractBaseUser, UserManager, Group
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from lego.users.managers import AbakusGroupManager
from .validators import username_validator


class AbakusGroup(PersistentModel):
    objects = AbakusGroupManager()

    name = models.CharField(_('name'), max_length=80, unique=True)
    description = models.CharField(_('description'), blank=True, max_length=200)
    parent = models.ForeignKey('self', blank=True, null=True, verbose_name=_('parent'),
                               related_name='children')

    permission_groups = models.ManyToManyField(
        Group,
        verbose_name=_('permission groups'),
        related_name='abakus_groups',
        blank=True,
        null=True
    )

    class Meta:
        unique_together = 'name',
        verbose_name = _('abakus group')
        verbose_name_plural = _('abakus groups')
        permissions = (
            ('retrieve_abakusgroup', 'Can retrieve AbakusGroups'),
            ('list_abakusgroup', 'Can list AbakusGroups')
        )

    @property
    def is_committee(self):
        if self.parent:
            return self.parent.name == 'Abakom'
        return False

    @property
    def is_root_node(self):
        return not self.parent

    def get_ancestors(self, include_self=False):
        abakus_groups = []

        if include_self:
            abakus_groups.append(self)

        if self.parent:
            abakus_groups.extend(self.parent.get_ancestors(True))

        return abakus_groups

    def get_descendants(self, include_self=False):
        abakus_groups = []

        if include_self:
            abakus_groups.append(self)

        for child in self.children.all():
            abakus_groups.extend(child.get_descendants(True))

        return abakus_groups

    def add_user(self, user, **kwargs):
        membership = Membership(user=user, abakus_group=self, **kwargs)
        membership.save()

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name.lower(),


def _user_get_all_permissions(user, obj):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, 'get_all_permissions'):
            permissions.update(backend.get_all_permissions(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    for backend in auth.get_backends():
        if hasattr(backend, 'has_perm'):
            if backend.has_perm(user, perm, obj):
                return True
    return False


def _user_has_module_perms(user, app_label):
    for backend in auth.get_backends():
        if hasattr(backend, 'has_module_perms'):
            if backend.has_module_perms(user, app_label):
                return True
    return False


class PermissionsMixin(models.Model):
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.')
    )
    abakus_groups = models.ManyToManyField(
        AbakusGroup,
        through='Membership',
        through_fields=('user', 'abakus_group'),
        verbose_name=_('abakus groups'),
        blank=True, help_text=_('The groups this user belongs to. A user will '
                                'get all permissions granted to each of their groups.'),
        related_name='users',
        related_query_name='user'
    )

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through their
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, 'get_group_permissions'):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        }
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = ('retrieve_user', 'Can retrieve user'), ('list_user', 'Can list users')

    @cached_property
    def all_groups(self):
        own_groups = set()

        for group in self.abakus_groups.all():
            if group not in own_groups:
                own_groups = own_groups.union(set(group.get_ancestors(True)))

        return list(own_groups)

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name).strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def natural_key(self):
        return self.username,


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

    user = models.ForeignKey(User, verbose_name=_('user'))
    abakus_group = models.ForeignKey(AbakusGroup, verbose_name=_('abakus group'))

    role = models.CharField(_('role'), max_length=2, choices=ROLES, default=MEMBER)
    is_active = models.BooleanField(_('is active'), default=True)

    start_date = models.DateField(_('start date'), auto_now_add=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)

    class Meta:
        unique_together = ('user', 'abakus_group')

    def __str__(self):
        return '{0} is {1} in {2}'.format(self.user, self.get_role_display(), self.abakus_group)
