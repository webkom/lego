from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin as DjangoPermissionMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.utils import timezone
from django.utils.functional import cached_property
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lego.apps.external_sync.models import GSuiteAddress, PasswordHashUser
from lego.apps.files.models import FileField
from lego.apps.permissions.validators import KeywordPermissionValidator
from lego.apps.users import constants
from lego.apps.users.managers import (
    AbakusGroupManager, AbakusGroupManagerWithoutText, AbakusUserManager, MembershipManager,
    UserPenaltyManager
)
from lego.apps.users.permissions import (
    AbakusGroupPermissionHandler, MembershipPermissionHandler, UserPermissionHandler
)
from lego.utils.models import BasisModel, PersistentModel
from lego.utils.validators import ReservedNameValidator

from .validators import email_blacklist_validator, username_validator


class MembershipHistory(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    abakus_group = models.ForeignKey('users.AbakusGroup', on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=constants.ROLES, default=constants.MEMBER)
    start_date = models.DateField(null=True)
    end_date = models.DateField()


class Membership(BasisModel):
    objects = MembershipManager()

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    abakus_group = models.ForeignKey('users.AbakusGroup', on_delete=models.CASCADE)

    role = models.CharField(max_length=30, choices=constants.ROLES, default=constants.MEMBER)
    is_active = models.BooleanField(default=True, db_index=True)
    email_lists_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'abakus_group')
        permission_handler = MembershipPermissionHandler()

    def delete(self, using=None, force=False):
        with transaction.atomic():
            MembershipHistory.objects.create(
                user=self.user, abakus_group=self.abakus_group, role=self.role,
                start_date=self.created_at, end_date=timezone.now()
            )
            super(Membership, self).delete(using=using, force=True)

    def __str__(self):
        return f'{self.user} is {self.get_role_display()} in {self.abakus_group}'


class AbakusGroup(MPTTModel, PersistentModel):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    description = models.CharField(blank=True, max_length=200)
    contact_email = models.EmailField(blank=True)
    parent = TreeForeignKey(
        'self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL
    )
    logo = FileField(related_name='group_pictures')
    type = models.CharField(
        max_length=10, choices=constants.GROUP_TYPES, default=constants.GROUP_OTHER
    )
    text = models.TextField(blank=True)

    permissions = ArrayField(
        models.CharField(validators=[KeywordPermissionValidator()], max_length=50),
        verbose_name='permissions', default=[]
    )

    objects = AbakusGroupManagerWithoutText()
    objects_with_text = AbakusGroupManager()

    class Meta:
        permission_handler = AbakusGroupPermissionHandler()

    def __str__(self):
        return self.name

    @property
    def is_committee(self):
        return self.type == constants.GROUP_COMMITTEE

    @property
    def is_grade(self):
        return self.type == constants.GROUP_GRADE

    @property
    def leader(self):
        """Assume there is only one leader, or that we don't care about which leader we get
        if there is multiple leaders"""
        membership = self.memberships.filter(role='leader').first()
        if membership:
            return membership.user
        return None

    @cached_property
    def memberships(self):
        descendants = self.get_descendants(True)
        return Membership.objects.filter(
            deleted=False,
            is_active=True,
            user__abakus_groups__in=descendants,
            abakus_group__in=descendants,
        )

    @cached_property
    def number_of_users(self):
        return self.memberships.distinct('user').count()

    def add_user(self, user, **kwargs):
        membership, _ = Membership.objects.update_or_create(
            user=user, abakus_group=self, defaults={
                "deleted": False,
                **kwargs
            }
        )
        return membership

    def remove_user(self, user):
        membership = Membership.objects.get(user=user, abakus_group=self)
        membership.delete()

    def natural_key(self):
        return self.name,

    def restricted_lookup(self):
        """
        Restricted Mail
        """
        memberships = self.memberships
        return [membership.user for membership in memberships], []

    def announcement_lookup(self):
        memberships = self.memberships
        return [membership.user for membership in memberships]


class PermissionsMixin(models.Model):

    abakus_groups = models.ManyToManyField(
        AbakusGroup, through='Membership', through_fields=('user', 'abakus_group'), blank=True,
        help_text='The groups this user belongs to. A user will '
        'get all permissions granted to each of their groups.', related_name='users',
        related_query_name='user'
    )

    @cached_property
    def is_superuser(self):
        return '/sudo/' in self.get_all_permissions()

    is_staff = is_superuser

    @property
    def is_abakus_member(self):
        for group in self.all_groups:
            if group.name == constants.MEMBER_GROUP:
                return True
        return False

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
    def memberships(self):
        return Membership.objects.filter(
            deleted=False,
            is_active=True,
            user=self,
        )

    @cached_property
    def all_groups(self):
        groups = set()

        memberships = self.memberships.filter(
            deleted=False,
            is_active=True,
        ).select_related('abakus_group')

        for membership in memberships:
            if membership.abakus_group not in groups:
                groups.add(membership.abakus_group)
                groups.update(membership.abakus_group.get_ancestors())

        return list(groups)


class User(PasswordHashUser, GSuiteAddress, AbstractBaseUser, PersistentModel, PermissionsMixin):
    """
    Abakus user model, uses AbstractBaseUser because we use a custom PermissionsMixin.
    """
    username = models.CharField(
        max_length=50, unique=True, db_index=True,
        help_text='Required. 50 characters or fewer. Letters, digits and _ only.',
        validators=[username_validator, ReservedNameValidator()], error_messages={
            'unique': 'A user with that username already exists.',
        }
    )
    student_username = models.CharField(
        max_length=30, unique=True, null=True,
        help_text='30 characters or fewer. Letters, digits and _ only.',
        validators=[username_validator, ReservedNameValidator()], error_messages={
            'unique': 'A user has already verified that student username.',
        }
    )
    first_name = models.CharField('first name', max_length=50, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    allergies = models.CharField('allergies', max_length=30, blank=True)
    email = models.EmailField(
        unique=True, validators=[email_blacklist_validator], error_messages={
            'unique': 'A user with that email already exists.',
        }
    )
    email_lists_enabled = models.BooleanField(default=True)
    gender = models.CharField(max_length=50, choices=constants.GENDERS)
    picture = FileField(related_name='user_pictures')
    is_active = models.BooleanField(
        default=True, help_text='Designates whether this user should be treated as '
        'active. Unselect this instead of deleting accounts.'
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = AbakusUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    backend = 'lego.apps.permissions.backends.AbakusPermissionBackend'
    unanswered_surveys = ArrayField(models.IntegerField(), default=[])

    class Meta:
        permission_handler = UserPermissionHandler()

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
        return self.abakus_groups.filter(type=constants.GROUP_GRADE).first()

    @property
    def profile_picture(self):
        return self.picture_id or self.get_default_picture()

    @property
    def email_address(self):
        """
        Return the address used to reach the user. Some users have a GSuite address and this
        function is used to decide the correct address to use.
        """
        internal_address = self.internal_email_address

        if self.is_active and self.crypt_password_hash and internal_address:
            # Return the internal address if all requirements for a GSuite account are met.
            return internal_address
        return self.email

    def update_unanswered_surveys(self):
        # TODO: optimize and test properly
        from lego.apps.surveys.models import Survey
        active_surveys = Survey.objects.filter(active_from__lte=timezone.now())\
            .filter(template_type__isnull=True)
        unanswered_surveys = filter(
            lambda survey:
                len(survey.submissions.all()) != survey.event.registrations.filter(
                    presence='PRESENT'
                )
                and survey.event.registrations.filter(user=self).exists(),
            active_surveys.all()
        )
        self.unanswered_surveys = list(map(lambda survey: survey.id, unanswered_surveys))
        self.save()

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

    def restricted_lookup(self):
        """
        Restricted mail
        """
        return [self], []

    def announcement_lookup(self):
        return [self]


class Penalty(BasisModel):

    user = models.ForeignKey(User, related_name='penalties', on_delete=models.CASCADE)
    reason = models.CharField(max_length=1000)
    weight = models.IntegerField(default=1)
    source_event = models.ForeignKey(
        'events.Event', related_name='penalties', on_delete=models.CASCADE
    )

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
