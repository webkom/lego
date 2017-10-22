from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from lego.apps.users.constants import ROLES
from lego.utils.validators import ReservedNameValidator


class EmailAddress(models.Model):
    """
    Only store the local part, append the domain based on the GSUITE_DOMAIN setting.
    """

    email = models.CharField(
        max_length=128,
        primary_key=True,
        validators=[
            RegexValidator(regex=EmailValidator.user_regex),
            ReservedNameValidator()
        ]
    )

    def is_assigned(self, new_owner=None):
        """
        Use the new_owner to make the validation pass with the same as the current owner.
        """
        fields = ['email_list', 'user', 'abakusgroup']

        def check_reverse(field):
            try:
                owner = getattr(self, field, None)
                if owner and new_owner:
                    return not owner == new_owner
                elif owner:
                    return True
            except ObjectDoesNotExist:
                pass

        for field in fields:
            if check_reverse(field):
                return True

        return False


class EmailList(models.Model):

    name = models.CharField(max_length=64)
    email = models.OneToOneField(EmailAddress, related_name='email_list', editable=False)

    users = models.ManyToManyField('users.User', related_name='email_lists', blank=True)

    group_roles = ArrayField(models.CharField(max_length=64, choices=ROLES), default=list)
    groups = models.ManyToManyField('users.AbakusGroup', related_name='email_lists', blank=True)

    @property
    def email_address(self):
        return f'{self.email_id}@{settings.GSUITE_DOMAIN}'

    def members(self):
        """
        Return addresses to the members.
        """

        members = []
        users = self.users.filter(email_lists_enabled=True)
        groups = self.groups.all()

        members += [user.email_address for user in users]

        for group in groups:
            if not self.group_roles:
                memberships = group.memberships.filter(
                    email_lists_enabled=True,
                    user__email_lists_enabled=True,
                )
            else:
                memberships = group.memberships.filter(
                    email_lists_enabled=True,
                    user__email_lists_enabled=True,
                    role__in=self.group_roles,
                )
            members += [membership.user.email_address for membership in memberships]

        return list(set(members))
