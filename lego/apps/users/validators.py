from django.core import validators

username_validator = validators.RegexValidator(
    r'^[a-z0-9-._]+$',
    'Enter a valid username.  This value may contain only letters, numbers and ./-/_ '
    'characters.',
    'invalid'
)

student_username_validator = validators.RegexValidator(
    r'^[a-z0-9-._]+$',
    'Enter a valid username.  This value may contain only letters, numbers and ./-/_ '
    'characters.',
    'invalid'
)
