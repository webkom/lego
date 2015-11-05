from basis.models import BasisModel, PersistentModel
from django.contrib import auth
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lego.permissions.validators import KeywordPermissionValidator
from lego.users.managers import AbakusGroupManager, MembershipManager, UserManager

from .validators import username_validator


class AbakusGroup(MPTTModel, PersistentModel):
    objects = AbakusGroupManager()

    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(blank=True, max_length=200)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')
    permissions = ArrayField(
        models.CharField(validators=[KeywordPermissionValidator()],
                         max_length=30),
        verbose_name='permissions', default=list
    )

    class Meta:
        unique_together = 'name',

    @property
    def is_committee(self):
        if self.parent:
            return self.parent.name == 'Abakom'
        return False

    def add_user(self, user, **kwargs):
        membership = Membership(user=user, abakus_group=self, **kwargs)
        membership.save()

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name.lower(),


class PermissionsMixin(models.Model):
    abakus_groups = models.ManyToManyField(
        AbakusGroup,
        through='Membership',
        through_fields=('user', 'abakus_group'),
        blank=True, help_text=_('The groups this user belongs to. A user will '
                                'get all permissions granted to each of their groups.'),
        related_name='users',
        related_query_name='user'
    )

    class Meta:
        abstract = True

    def get_permissions(self):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, 'get_all_permissions'):
                permissions.update(backend.get_all_permissions(self))

        return permissions

    def has_perm(self, perm):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general.
        """

        for backend in auth.get_backends():
            if hasattr(backend, 'has_perm'):
                if backend.has_perm(self, perm):
                    return True


class User(AbstractBaseUser, PersistentModel, PermissionsMixin):
    username = models.CharField(
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
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @cached_property
    def all_groups(self):
        own_groups = set()

        for group in self.abakus_groups.all():
            if group not in own_groups:
                own_groups.add(group)
                own_groups = own_groups.union(set(group.get_ancestors()))

        return list(own_groups)

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name).strip()

    @property
    def full_name(self):
        return self.get_full_name()

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

    objects = MembershipManager()

    user = models.ForeignKey(User)
    abakus_group = models.ForeignKey(AbakusGroup)

    role = models.CharField(max_length=2, choices=ROLES, default=MEMBER)
    is_active = models.BooleanField(default=True)

    start_date = models.DateField(auto_now_add=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'abakus_group')

    def __str__(self):
        return '{0} is {1} in {2}'.format(self.user, self.get_role_display(), self.abakus_group)
