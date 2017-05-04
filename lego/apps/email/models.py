from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator
from django.db import models


class EmailAddress(models.Model):
    email = models.CharField(max_length=128, null=False, primary_key=True,
                             validators=[EmailValidator(whitelist=[settings.GSUITE_DOMAIN])])

    @property
    def is_assigned(self):
        try:
            if self.email_list: return True
        except ObjectDoesNotExist:
            pass

        try:
            if self.user: return True
        except ObjectDoesNotExist:
            return False


class EmailList(models.Model):
    users = models.ManyToManyField('users.User', related_name='email_lists', blank=True)
    groups = models.ManyToManyField('users.AbakusGroup', related_name='email_lists', blank=True)

    email_address = models.OneToOneField(EmailAddress, related_name='email_list')

    # TODO: Remove hack
    @property
    def name(self):
        return 'name'

    def __str__(self):
        return self.email_address.email
