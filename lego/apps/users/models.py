from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import PermissionsMixin as DjangoPermissionMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lego.apps.permissions.validators import KeywordPermissionValidator
from lego.apps.users.managers import (AbakusGroupManager, MembershipManager, UserManager,
                                      UserPenaltyManager)
from lego.utils.models import BasisModel, PersistentModel

from .validators import username_validator


class AbakusGroup(MPTTModel, PersistentModel):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    description = models.CharField(blank=True, max_length=200)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')

    permissions = ArrayField(
        models.CharField(validators=[KeywordPermissionValidator()], max_length=50),
        verbose_name='permissions', default=list
    )

    group_objects = AbakusGroupManager()

    def __str__(self):
        return self.name

    @property
    def is_committee(self):
        if self.parent:
            return self.parent.name == 'Abakom'
        return False

    @property
    def is_interest_group(self):
        if self.parent:
            return self.parent.name == 'Interessegrupper'
        return False

    @property
    def is_social_group(self):
        return self.is_committee or self.is_interest_group

    @cached_property
    def memberships(self):
        return Membership.objects.filter(user__abakus_groups__in=self.get_descendants(True)) \
            .distinct('user')

    @cached_property
    def number_of_users(self):
        return self.memberships.count()

    def add_user(self, user, **kwargs):
        membership = Membership(user=user, abakus_group=self, **kwargs)
        membership.save()

    def remove_user(self, user):
        membership = Membership.objects.get(user=user, abakus_group=self)
        membership.delete()

    def natural_key(self):
        return self.name


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

    @cached_property
    def is_superuser(self):
        return '/sudo/' in self.get_all_permissions()
    is_staff = is_superuser

    @property
    def is_abakus_member(self):
        return 'Abakus' in [group.name for group in self.all_groups]

    @property
    def is_abakom_member(self):
        return bool(filter(lambda group: group.is_committee, self.all_groups))

    @property
    def committees(self):
        return [group for group in self.all_groups if group.is_committee]

    @property
    def interest_groups(self):
        return [group for group in self.all_groups if group.is_interest_group]

    @property
    def social_groups(self):
        return [group for group in self.all_groups if group.is_social_group]

    get_group_permissions = DjangoPermissionMixin.get_group_permissions
    get_all_permissions = DjangoPermissionMixin.get_all_permissions
    has_module_perms = DjangoPermissionMixin.has_module_perms
    has_perms = DjangoPermissionMixin.has_perms
    has_perm = DjangoPermissionMixin.has_perm

    class Meta:
        abstract = True

    @cached_property
    def all_groups(self):
        own_groups = set()

        for group in self.abakus_groups.all():
            if group not in own_groups:
                own_groups.add(group)
                own_groups = own_groups.union(set(group.get_ancestors()))

        return list(own_groups)


class User(AbstractBaseUser, PersistentModel, PermissionsMixin):
    """
    Abakus user model, uses AbstractBaseUser because we use a custom PermissionsMixin.
    """
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
    is_active = models.BooleanField(
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    backend = 'lego.apps.permissions.backends.AbakusPermissionBackend'

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

    def number_of_penalties(self):
        # Returns the total penalty weight for this user
        count = Penalty.objects.valid().filter(user=self)\
            .aggregate(models.Sum('weight'))['weight__sum']
        return count or 0


class Membership(BasisModel):
    MEMBER = 'member'
    LEADER = 'leader'
    CO_LEADER = 'co-leader'
    TREASURER = 'treasurer'

    ROLES = (
        (MEMBER, _('Member')),
        (LEADER, _('Leader')),
        (CO_LEADER, _('Co-Leader')),
        (TREASURER, _('Treasurer'))
    )

    objects = MembershipManager()

    user = models.ForeignKey(User)
    abakus_group = models.ForeignKey(AbakusGroup)

    role = models.CharField(max_length=20, choices=ROLES, default=MEMBER)
    is_active = models.BooleanField(default=True)

    start_date = models.DateField(auto_now_add=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'abakus_group')

    def __str__(self):
        return '{0} is {1} in {2}'.format(self.user, self.get_role_display(), self.abakus_group)


class Penalty(BasisModel):

    user = models.ForeignKey(User, related_name='penalties')
    reason = models.CharField(max_length=1000)
    weight = models.IntegerField(default=1)
    source_event = models.ForeignKey('events.Event', related_name='penalties')

    objects = UserPenaltyManager()

    def expires(self):
        dt = Penalty.penalty_offset(self.created_at) - (timezone.now() - self.created_at)
        return dt.days

    @staticmethod
    def penalty_offset(start_date, forwards=True):

        remaining_days = settings.PENALTY_DURATION.days
        offset_days = 0
        multiplier = 1 if forwards else -1

        while remaining_days > 0:

            date_to_check = start_date + (multiplier * timedelta(days=offset_days))

            if not Penalty.ignore_date(date_to_check):
                remaining_days -= 1

            offset_days += 1

        return timedelta(days=offset_days)

    @staticmethod
    def ignore_date(date):
        summer_from, summer_to = settings.PENALTY_IGNORE_SUMMER
        winter_from, winter_to = settings.PENALTY_IGNORE_WINTER
        if summer_from \
                < (date.month, date.day) \
                < summer_to:
            return True
        elif winter_to \
                < (date.month, date.day) \
                <= winter_from:
            return False
        return True
