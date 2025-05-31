from django.core.validators import RegexValidator
from django.utils.regex_helper import _lazy_re_compile

slug_re = _lazy_re_compile(r"^[-a-zA-ZæøåÆØÅ0-9:]+\Z")
validate_tag = RegexValidator(
    slug_re, "Enter a valid 'tag' consisting only of letters and numbers.", "invalid"
)
