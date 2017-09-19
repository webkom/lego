from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
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
class EmailValidatorWithBlacklist:
    """
    Takes a blacklist argument and raises an ValueError if the domainpart of the address exists
    in the blacklist.
    """

    code = 'invalid'
    domain_blacklist = []

    def __init__(self, blacklist=None, *args, **kwargs):
        if blacklist is not None:
            self.domain_blacklist = blacklist

    def __call__(self, value):
        _, domain_part = value.rsplit('@', 1)

        if domain_part.lower() in self.domain_blacklist:
            message = 'You can\'t use a {} email for your personal account.'.format(domain_part)
            raise ValidationError(message, code=self.code)

    def __eq__(self, other):
        return self.domain_blacklist == other.domain_blacklist and super().__eq__(other)


# We do not permit emails from our GSuite account - causes circular dependencies.
email_blacklist_validator = EmailValidatorWithBlacklist(blacklist=[settings.GSUITE_DOMAIN])
