from django.core.validators import RegexValidator, _lazy_re_compile

slug_re = _lazy_re_compile(r'^[-a-z0-9æøå_.#%$&/]+\Z')
validate_tag = RegexValidator(
    slug_re,
    "Enter a valid 'tag' consisting of letters, numbers, underscores or hyphens.",
    'invalid'
)
