from django.conf import settings
from django.core.validators import EmailValidator
from django.db import models


class EmailAddress(models.Model):
    email = models.CharField(max_length=128, null=False, unique=True,
                             validators=[EmailValidator(whitelist=[settings.GSUITE_DOMAIN])])

    def is_assigned(self):
        return self.email_list is not None or self.user is not None


class EmailList(models.Model):
    users = models.ManyToManyField('users.User', related_name='email_lists')
    groups = models.ManyToManyField('users.AbakusGroup', related_name='email_lists')

    email_address = models.OneToOneField(EmailAddress, related_name='email_list')

    # TODO: Remove hack
    @property
    def name(self):
        return 'name'

    def __str__(self):
        return self.email_address.email
