from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator
from django.db import models

from .utils.ldap import create_ldap_password_hash


class LDAPUser(models.Model):
    """
    We don't have the user password as plaintext.
    This model stores the password hash each time the user changes password.
    """

    ldap_password_hash = models.CharField(max_length=256)

    class Meta:
        abstract = True

    def set_password(self, password):
        super().set_password(password)
        self.ldap_password_hash = create_ldap_password_hash(password)

