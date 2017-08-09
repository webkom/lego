from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator

from lego.utils.validators import ReservedNameValidator


def validate_email_address(email_address):

    if email_address.is_assigned():
        raise ValidationError('The address is already assigned')


def validate_email_address_content(email_address):
    """Make sure we only create valid emails."""

    regex_validator = RegexValidator(regex=EmailValidator.user_regex)
    reserved_valdator = ReservedNameValidator()

    regex_validator(email_address.email)
    reserved_valdator(email_address.email)
