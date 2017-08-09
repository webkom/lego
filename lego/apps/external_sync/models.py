from django.conf import settings
from django.db import models

from .utils.password import create_password_hash


class PasswordHashUser(models.Model):
    """
    We don't have the user password as plaintext.
    This model stores the password hash each time the user changes password.
    The password_hash property are used by both LDAP and GSuite.
    """

    crypt_password_hash = models.CharField(max_length=1024)

    class Meta:
        abstract = True

    def set_password(self, password):
        super().set_password(password)
        self.crypt_password_hash = create_password_hash(password)


class GSuiteAddress(models.Model):
    """
    Users with an internal_email and internal_email_enabled=True have access to our GSuite.
    Don't change the internal_email after the user have received an account!
    """

    internal_email = models.OneToOneField(
        'email.EmailAddress',
        related_name='%(class)s', null=True,
        on_delete=models.SET_NULL, editable=False
    )
    internal_email_enabled = models.BooleanField(default=True)

    @property
    def internal_email_address(self):
        internal_email = self.internal_email_id
        if internal_email and settings.GSUITE_DOMAIN and self.internal_email_enabled:
            return f'{internal_email}@{settings.GSUITE_DOMAIN}'

    class Meta:
        abstract = True
