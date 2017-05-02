from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import PermissionsMixin as DjangoPermissionMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lego.apps.external_sync.models import LDAPUser
from lego.apps.files.models import FileField
from lego.apps.permissions.validators import KeywordPermissionValidator
from lego.apps.users import constants
from lego.apps.users.managers import (AbakusGroupManager, AbakusUserManager, MembershipManager,
                                      UserPenaltyManager)
from lego.utils.models import BasisModel, PersistentModel

from .validators import student_username_validator, username_validator


class AbakusGroup(MPTTModel, PersistentModel):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    description = models.CharField(blank=True, max_length=200)
    is_grade = models.BooleanField(default=False)
    is_committee = models.BooleanField(default=False)
    is_interest_group = models.BooleanField(default=False)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')

    permissions = ArrayField(
        models.CharField(validators=[KeywordPermissionValidator()], max_length=50),
        verbose_name='permissions', default=list
    )

    objects = AbakusGroupManager()

    def __str__(self):
        return self.name

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
        return self.name,


class PermissionsMixin(models.Model):

    abakus_groups = models.ManyToManyField(
        AbakusGroup,
        through='Membership',
        through_fields=('user', 'abakus_group'),
        blank=True, help_text='The groups this user belongs to. A user will '
                              'get all permissions granted to each of their groups.',
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
        # from first_true @ https://docs.python.org/3/library/itertools.html
        return bool(next(filter(lambda group: group.is_committee, self.all_groups), False))

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


class User(LDAPUser, AbstractBaseUser, PersistentModel, PermissionsMixin):
    """
    Abakus user model, uses AbstractBaseUser because we use a custom PermissionsMixin.
    """
    username = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': 'A user with that username already exists.',
        }
    )
    student_username = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        help_text='30 characters or fewer. Letters, digits and ./-/_ only.',
        validators=[student_username_validator],
        error_messages={
            'unique': 'A user has already verified that student username.',
        }
    )
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    allergies = models.CharField('allergies', max_length=30, blank=True)
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with that email already exists.',
        }
    )
    gender = models.CharField(max_length=50, choices=constants.GENDERS)
    picture = FileField(related_name='user_pictures')
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as '
                  'active. Unselect this instead of deleting accounts.'
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = AbakusUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    backend = 'lego.apps.permissions.backends.AbakusPermissionBackend'

    def clean(self):
        self.student_username = self.student_username.lower()
        super(User, self).clean()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_default_picture(self):
        if self.gender == constants.MALE:
            return 'default_male_avatar.png'
        elif self.gender == constants.FEMALE:
            return 'default_female_avatar.png'
        else:
            return 'default_other_avatar.png'

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def grade(self):
        return self.abakus_groups.filter(is_grade=True).first()

    @property
    def profile_picture(self):
        return self.picture_id or self.get_default_picture()

    @profile_picture.setter
    def profile_picture(self, value):
        self.picture = value

    def is_verified_student(self):
        return self.student_username is not None

    def get_short_name(self):
        return self.first_name

    def natural_key(self):
        return self.username,

    def number_of_penalties(self):
        # Returns the total penalty weight for this user
        count = Penalty.objects.valid().filter(user=self)\
            .aggregate(models.Sum('weight'))['weight__sum']
        return count or 0

    @staticmethod
    def generate_registration_token(email):
        return TimestampSigner().sign(signing.dumps({
            'email': email
        }))

    @staticmethod
    def validate_registration_token(token):
        try:
            return signing.loads(TimestampSigner().unsign(
                token,
                max_age=settings.REGISTRATION_CONFIRMATION_TIMEOUT
            ))['email']
        except (BadSignature, SignatureExpired):
            return None

    @staticmethod
    def generate_student_confirmation_token(student_username, course, member):
        data = signing.dumps({
            'student_username': student_username.lower(),
            'course': course,
            'member': member
        })
        token = TimestampSigner().sign(data)
        return token

    @staticmethod
    def validate_student_confirmation_token(token):
        try:
            return signing.loads(TimestampSigner().unsign(
                token,
                max_age=settings.STUDENT_CONFIRMATION_TIMEOUT
            ))
        except (BadSignature, SignatureExpired):
            return None


class Membership(BasisModel):
    objects = MembershipManager()

    user = models.ForeignKey(User)
    abakus_group = models.ForeignKey(AbakusGroup)

    role = models.CharField(max_length=20, choices=constants.ROLES, default=constants.MEMBER)
    is_active = models.BooleanField(default=True)

    start_date = models.DateField(auto_now_add=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'abakus_group')

    def __str__(self):
        return f'{self.user} is {self.get_role_display()} in {self.abakus_group}'


class Penalty(BasisModel):

    user = models.ForeignKey(User, related_name='penalties')
    reason = models.CharField(max_length=1000)
    weight = models.IntegerField(default=1)
    source_event = models.ForeignKey('events.Event', related_name='penalties')

    objects = UserPenaltyManager()

    def expires(self):
        dt = Penalty.penalty_offset(self.created_at) - (timezone.now() - self.created_at)
        return dt.days

    @property
    def exact_expiration(self):
        """ Returns the exact time of expiration """
        dt = Penalty.penalty_offset(self.created_at) - (timezone.now() - self.created_at)
        return timezone.now() + dt

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
