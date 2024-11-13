# mypy: ignore-errors
import operator

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin as DjangoPermissionMixin,
)
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import datetime, timedelta

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from phonenumber_field.modelfields import PhoneNumberField

from lego.apps.email.models import EmailList
from lego.apps.events.constants import PRESENCE_CHOICES
from lego.apps.external_sync.models import GSuiteAddress, PasswordHashUser
from lego.apps.files.models import FileField
from lego.apps.permissions.validators import KeywordPermissionValidator
from lego.apps.users import constants
from lego.apps.users.managers import (
    AbakusGroupManager,
    AbakusGroupManagerWithoutText,
    AbakusUserManager,
    MembershipManager,
    UserPenaltyManager,
)
from lego.apps.users.permissions import (
    AbakusGroupPermissionHandler,
    MembershipPermissionHandler,
    UserPermissionHandler,
)
from lego.utils.decorators import abakus_cached_property
from lego.utils.models import BasisModel, CachedModel, PersistentModel
from lego.utils.validators import ReservedNameValidator

from .validators import (
    email_blacklist_validator,
    github_username_validator,
    linkedin_id_validator,
    student_username_validator,
    username_validator,
)


class MembershipHistory(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    abakus_group = models.ForeignKey("users.AbakusGroup", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=30, choices=constants.ROLES, default=constants.MEMBER
    )
    start_date = models.DateField(null=True)
    end_date = models.DateField()


class Membership(BasisModel):
    objects = MembershipManager()  # type: ignore

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    abakus_group = models.ForeignKey("users.AbakusGroup", on_delete=models.CASCADE)

    role = models.CharField(
        max_length=30, choices=constants.ROLES, default=constants.MEMBER
    )
    is_active = models.BooleanField(default=True, db_index=True)
    email_lists_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "abakus_group")
        permission_handler = MembershipPermissionHandler()

    def delete(self, using=None, force=False):
        with transaction.atomic():
            MembershipHistory.objects.create(
                user=self.user,
                abakus_group=self.abakus_group,
                role=self.role,
                start_date=self.created_at,
                end_date=timezone.now(),
            )
            super(Membership, self).delete(using=using, force=True)

    def __str__(self):
        return f"{self.user} is {self.get_role_display()} in {self.abakus_group}"


class AbakusGroup(MPTTModel, PersistentModel):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    description = models.CharField(blank=True, max_length=200)
    contact_email = models.EmailField(blank=True)
    parent = TreeForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    logo = FileField(related_name="group_pictures")
    type = models.CharField(
        max_length=10, choices=constants.GROUP_TYPES, default=constants.GROUP_OTHER
    )
    text = models.TextField(blank=True)

    permissions = ArrayField(
        models.CharField(validators=[KeywordPermissionValidator()], max_length=50),
        verbose_name="permissions",
        default=list,
        blank=True,
    )

    objects = AbakusGroupManagerWithoutText()
    objects_with_text = AbakusGroupManager()

    show_badge = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

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
        membership = self.memberships.filter(role="leader").first()
        if membership:
            return membership.user
        return None

    @abakus_cached_property
    def memberships(self):
        descendants = self.get_descendants(True)
        return Membership.objects.filter(
            deleted=False,
            is_active=True,
            user__abakus_groups__in=descendants,
            abakus_group__in=descendants,
        )

    @abakus_cached_property
    def parent_permissions(self):
        parent_permissions = []
        for group in self.get_ancestors():
            parent_permissions += [
                {
                    "abakusGroup": {"id": group.pk, "name": group.name},
                    "permissions": group.permissions,
                }
            ]
        return parent_permissions

    @abakus_cached_property
    def number_of_users(self) -> int:
        return self.memberships.distinct("user").count()

    def add_user(self, user, **kwargs):
        membership, _ = Membership.objects.update_or_create(
            user=user, abakus_group=self, defaults={"deleted": False, **kwargs}
        )
        return membership

    def remove_user(self, user):
        membership = Membership.objects.get(user=user, abakus_group=self)
        membership.delete()

    def natural_key(self):
        return (self.name,)

    def restricted_lookup(self):
        """
        Restricted Mail
        """
        memberships = self.memberships.filter(email_lists_enabled=True)
        return [membership.user for membership in memberships], []

    def announcement_lookup(self):
        memberships = self.memberships
        return [membership.user for membership in memberships]


class PermissionsMixin(CachedModel):
    abakus_groups = models.ManyToManyField(
        AbakusGroup,
        through="Membership",
        through_fields=("user", "abakus_group"),
        blank=True,
        help_text="The groups this user belongs to. A user will "
        "get all permissions granted to each of their groups.",
        related_name="users",
        related_query_name="user",
    )

    @abakus_cached_property
    def is_superuser(self):
        return "/sudo/" in self.get_all_permissions()

    is_staff = property(operator.attrgetter("is_superuser"))

    @property
    def is_abakus_member(self):
        return self.abakus_groups.all().filter(name=constants.MEMBER_GROUP).exists()

    @property
    def is_abakom_member(self):
        # from first_true @ https://docs.python.org/3/library/itertools.html
        return bool(
            next(filter(lambda group: group.is_committee, self.all_groups), False)
        )

    @property
    def has_grade_group(self):
        return self.abakus_groups.filter(type=constants.GROUP_GRADE).exists()

    get_group_permissions = DjangoPermissionMixin.get_group_permissions
    get_all_permissions = DjangoPermissionMixin.get_all_permissions
    has_module_perms = DjangoPermissionMixin.has_module_perms
    has_perms = DjangoPermissionMixin.has_perms
    has_perm = DjangoPermissionMixin.has_perm

    class Meta:
        abstract = True

    @abakus_cached_property
    def memberships(self):
        return Membership.objects.filter(
            abakus_group__deleted=False, is_active=True, user=self
        )

    @abakus_cached_property
    def past_memberships(self):
        return MembershipHistory.objects.filter(
            user=self, abakus_group__deleted=False
        ).select_related("abakus_group")

    @abakus_cached_property
    def abakus_email_lists(self):
        email_filter = Q(users__in=[self])

        for membership, groups in self.all_groups_from_memberships.items():
            email_filter |= Q(
                groups__in=groups, group_roles__contains=[membership.role]
            ) | Q(groups__in=groups, group_roles=[])

        if not self.internal_email_address:
            email_filter &= Q(require_internal_address=False)

        return EmailList.objects.filter(email_filter).distinct()

    @abakus_cached_property
    def permissions_per_group(self):
        permissions_per_group = []
        for membership, groups in self.all_groups_from_memberships.items():
            parent_permissions = []
            for group in groups:
                if group.id is membership.abakus_group.id:
                    continue
                parent_permissions += [
                    {
                        "abakusGroup": {"id": group.pk, "name": group.name},
                        "permissions": group.permissions,
                    }
                ]
            permissions_per_group += [
                {
                    "abakusGroup": {
                        "id": membership.abakus_group.pk,
                        "name": membership.abakus_group.name,
                    },
                    "permissions": membership.abakus_group.permissions,
                    "parentPermissions": parent_permissions,
                }
            ]

        return permissions_per_group

    @abakus_cached_property
    def all_groups_from_memberships(self):
        # Mapping from membership to all ancestor groups, with the root
        # node first (inclusive group from membership)
        mapping = {}

        memberships = self.memberships.filter(
            abakus_group__deleted=False, deleted=False, is_active=True
        ).select_related("abakus_group")

        for membership in memberships:
            mapping[membership] = list(membership.abakus_group.get_ancestors()) + [
                membership.abakus_group,
            ]
        return mapping

    @abakus_cached_property
    def all_groups(self):
        all_groups = set()
        for groups in self.all_groups_from_memberships.values():
            all_groups.update(groups)
        return list(all_groups)


class User(
    PasswordHashUser, GSuiteAddress, AbstractBaseUser, PersistentModel, PermissionsMixin
):
    """
    Abakus user model, uses AbstractBaseUser because we use a custom PermissionsMixin.
    """

    username = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Required. 50 characters or fewer. Letters, digits and _ only.",
        validators=[username_validator, ReservedNameValidator()],
        error_messages={"unique": "A user with that username already exists."},
    )
    student_username = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        help_text="30 characters or fewer. Letters, digits and _ only.",
        validators=[student_username_validator, ReservedNameValidator()],
        error_messages={"unique": "A user has already verified that student username."},
    )
    student_verification_status = models.BooleanField(null=True, blank=True)
    first_name = models.CharField("first name", max_length=50, blank=False)
    last_name = models.CharField("last name", max_length=30, blank=False)
    allergies = models.CharField("allergies", max_length=500, blank=True)
    selected_theme = models.CharField(
        "selected theme",
        max_length=50,
        blank=False,
        choices=constants.THEMES,
        default=constants.AUTO_THEME,
    )
    email = models.EmailField(
        unique=True,
        validators=[email_blacklist_validator],
        error_messages={"unique": "A user with that email already exists."},
    )
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    email_lists_enabled = models.BooleanField(default=True)
    gender = models.CharField(max_length=50, choices=constants.GENDERS)
    picture = FileField(related_name="user_pictures", blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as "
        "active. Unselect this instead of deleting accounts.",
    )
    inactive_notified_counter = models.IntegerField(default=0)
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    date_bumped = models.DateTimeField("date bumped", null=True, default=None)

    github_username = models.CharField(
        max_length=39,
        unique=False,
        null=True,
        help_text="Enter a valid username.",
        validators=[github_username_validator, ReservedNameValidator()],
    )

    linkedin_id = models.CharField(
        max_length=71,
        unique=False,
        null=True,
        help_text="Enter a valid LinkedIn ID.",
        validators=[linkedin_id_validator, ReservedNameValidator()],
    )
    achievements_score = models.FloatField(default=0, null=False, blank=False)

    objects = AbakusUserManager()  # type: ignore

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    backend = "lego.apps.permissions.backends.AbakusPermissionBackend"

    class Meta:
        permission_handler = UserPermissionHandler()

    def clean(self):
        self.student_username = self.student_username.lower()
        super(User, self).clean()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_default_picture(self):
        if self.gender == constants.MALE:
            return "default_male_avatar.png"
        elif self.gender == constants.FEMALE:
            return "default_female_avatar.png"
        else:
            return "default_other_avatar.png"

    def delete(self, using=None, force=False):
        from lego.apps.events.models import Event

        if force:
            current_time = timezone.now()
            for event in Event.objects.filter(
                Q(registrations__user=self) & Q(registrations__pool__isnull=False)
            ):
                # If the event has been, add legacy count
                if event.unregistration_close_time < current_time:
                    event.add_legacy_registration()
                # Else unregister user
                else:
                    event.unregister(event.registrations.get(user=self))
        super(User, self).delete(using=using, force=force)

    def save(self, *args, **kwargs):
        from lego.apps.achievements.utils.calculation_utils import calculate_user_rank

        self.achievements_score = calculate_user_rank(self)
        super().save(*args, **kwargs)

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

    @profile_picture.setter  # type: ignore
    def profile_picture(self, value):
        self.picture = value

    def verify_student(self, feide_groups) -> bool:
        if self.is_verified_student():
            return True

        if self.has_grade_group:
            self.student_verification_status = True
            self.save()
            return True

        for group in feide_groups:
            if group["id"] in constants.FSGroup.values():
                grade_group = AbakusGroup.objects.get(
                    name=constants.AbakusGradeFSMapping[constants.FSGroup(group["id"])]
                )
                grade_group.add_user(self)
                self.student_verification_status = True
                self.save()
                try:
                    AbakusGroup.objects.get(name="Abakus").add_user(self)
                except AbakusGroup.DoesNotExist:
                    pass
                return True

        # Student has no allowed groups
        self.student_verification_status = False
        self.save()
        return False

    def is_verified_student(self):
        return self.student_verification_status

    def get_short_name(self):
        return self.first_name

    def natural_key(self):
        return (self.username,)

    def number_of_penalties(self) -> int:
        # Returns the total penalty weight for this user
        count = (
            Penalty.objects.valid()
            .filter(user=self)
            .aggregate(models.Sum("weight"))["weight__sum"]
        )
        return count or 0

    def has_registered_photo_consents_for_semester(
        self, event_year: int, event_semester: str
    ) -> bool:
        return not PhotoConsent.objects.filter(
            user=self,
            year=event_year,
            semester=event_semester,
            is_consenting__isnull=True,
        ).exists()

    def restricted_lookup(self):
        """
        Restricted mail
        """
        return [self], []

    def announcement_lookup(self):
        return [self]

    def unanswered_surveys(self) -> list:
        from lego.apps.events.models import Registration
        from lego.apps.surveys.models import Survey

        registrations = Registration.objects.filter(
            user_id=self.id, presence=PRESENCE_CHOICES.PRESENT
        )
        unanswered_surveys = (
            Survey.objects.filter(
                event__registrations__in=registrations,
                active_from__lte=timezone.now(),
                template_type__isnull=True,
            )
            .exclude(submissions__user__in=[self])
            .prefetch_related("event__registrations", "submissions__user")
        )
        return list(unanswered_surveys.values_list("id", flat=True))


class Penalty(BasisModel):
    user = models.ForeignKey(User, related_name="penalties", on_delete=models.CASCADE)
    reason = models.CharField(max_length=1000)
    weight = models.IntegerField(default=1)
    source_event = models.ForeignKey(
        "events.Event", related_name="penalties", on_delete=models.CASCADE
    )
    type = models.CharField(
        max_length=50,
        choices=constants.PENALTY_TYPES.choices,
        default=constants.PENALTY_TYPES.OTHER,
    )

    objects = UserPenaltyManager()  # type: ignore

    def expires(self):
        dt = Penalty.penalty_offset(self.created_at) - (
            timezone.now() - self.created_at
        )
        return dt.days

    @property
    def exact_expiration(self):
        """Returns the exact time of expiration"""
        dt = Penalty.penalty_offset(self.created_at) - (
            timezone.now() - self.created_at
        )
        return timezone.now() + dt

    @staticmethod
    def penalty_offset(start_date, forwards=True):
        remaining_days = settings.PENALTY_DURATION.days
        offset_days = 0
        multiplier = 1 if forwards else -1

        date_to_check = start_date + (multiplier * timedelta(days=offset_days))
        ignore_date = Penalty.ignore_date(date_to_check)
        while remaining_days > 0 or ignore_date:
            if not ignore_date:
                remaining_days -= 1

            offset_days += 1

            date_to_check = start_date + (multiplier * timedelta(days=offset_days))
            ignore_date = Penalty.ignore_date(date_to_check)

        return timedelta(days=offset_days)

    @staticmethod
    def ignore_date(date):
        summer_from, summer_to = settings.PENALTY_IGNORE_SUMMER
        winter_from, winter_to = settings.PENALTY_IGNORE_WINTER
        if summer_from <= (date.month, date.day) <= summer_to:
            return True
        elif winter_to < (date.month, date.day) < winter_from:
            return False
        return True


class PhotoConsent(BasisModel):
    user = models.ForeignKey(
        User, related_name="photo_consents", on_delete=models.CASCADE
    )
    semester = models.CharField(max_length=6, choices=constants.SEMESTERS)
    year = models.PositiveIntegerField()
    domain = models.CharField(choices=constants.PHOTO_CONSENT_DOMAINS, max_length=100)
    is_consenting = models.BooleanField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ("semester", "year", "domain", "user")

    @staticmethod
    def get_consents(user, *, time=None):
        now = timezone.now()
        consent_time = time if time is not None else now
        consent_semester = PhotoConsent.get_semester(consent_time)
        consent_year = consent_time.year

        # Don't create PhotoConsent objects for the past
        if consent_time >= now:
            PhotoConsent.objects.get_or_create(
                user=user,
                year=consent_year,
                semester=consent_semester,
                domain=constants.SOCIAL_MEDIA_DOMAIN,
            )

            PhotoConsent.objects.get_or_create(
                user=user,
                year=consent_year,
                semester=consent_semester,
                domain=constants.WEBSITE_DOMAIN,
            )
        if time is not None:
            return PhotoConsent.objects.filter(
                user=user, year=consent_year, semester=consent_semester
            )
        return PhotoConsent.objects.filter(user=user)

    @staticmethod
    def get_semester(time: datetime):
        return constants.AUTUMN if time.month > 7 else constants.SPRING
