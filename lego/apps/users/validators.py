from django.core import validators
from django.utils.translation import ugettext_lazy as _

username_validator = validators.RegexValidator(
    r'^[\w.@+-]+$',
    _('Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ '
      'characters.'),
    'invalid'
)
