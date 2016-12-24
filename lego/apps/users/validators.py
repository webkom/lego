from django.core import validators

username_validator = validators.RegexValidator(
    r'^[\w.@+-]+$',
    'Enter a valid username.  This value may contain only letters, numbers and @/./+/-/_ '
    'characters.',
    'invalid'
)
