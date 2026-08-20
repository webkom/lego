from django.core.validators import RegexValidator
from django.utils.regex_helper import _lazy_re_compile

slug_re = _lazy_re_compile(r"^(?:[^\W_]|[-:])+\Z")
validate_tag = RegexValidator(
    slug_re,
    "Enter a valid 'tag' consisting only of letters, numbers, hyphens and colons.",
    "invalid",
)
