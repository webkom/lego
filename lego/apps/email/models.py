from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator, RegexValidator
from django.db import models

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

    @property
    def is_assigned(self):
        try:
            if self.email_list or self.user or self.abakusgroup:
                return True
        except ObjectDoesNotExist:
            pass

        return False


class EmailList(models.Model):

    name = models.CharField(max_length=64)
    email = models.OneToOneField(EmailAddress, related_name='email_list')

    users = models.ManyToManyField('users.User', related_name='email_lists', blank=True)
    groups = models.ManyToManyField('users.AbakusGroup', related_name='email_lists', blank=True)

    @property
    def email_address(self):
        return f'{self.email_id}@{settings.GSUITE_DOMAIN}'

    def members(self):
        """
        Return addresses to the members.
        """

        members = []
        users = self.users.all()
        groups = self.groups.all()

        members += [user.email_address for user in users]

        for group in groups:
            members += [membership.user.email_address for membership in group.memberships]

        return members
