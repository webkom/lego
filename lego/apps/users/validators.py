from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.deconstruct import deconstructible

username_validator = validators.RegexValidator(
    r'^[\w.@+-]+$',
    'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ '
    'characters.',
    'invalid'
)

student_username_validator = validators.RegexValidator(
    r'^[a-z0-9-._]+$',
    'Enter a valid username.  This value may contain only letters, numbers and ./-/_ '
    'characters.',
    'invalid'
)


@deconstructible
class EmailValidatorWithBlacklist(EmailValidator):
    """
    Takes a blacklist argument and raises an ValueError if the domainpart of the address exists
    in the blacklist.
    """

    domain_blacklist = []

    def __init__(self, blacklist=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if blacklist is not None:
            self.domain_blacklist = blacklist

    def __call__(self, value):
        super().__call__(value)

        _, domain_part = value.rsplit('@', 1)

        if domain_part.lower() in self.domain_blacklist:
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return self.domain_blacklist == other.domain_blacklist and super().__eq__(other)


# We do not permit emails from our GSuite account - causes circular dependencies.
email_validator = EmailValidatorWithBlacklist(blacklist=[settings.GSUITE_DOMAIN])
