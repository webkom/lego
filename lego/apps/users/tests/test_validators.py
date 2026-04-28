from django.core.exceptions import ValidationError

from lego.apps.users.validators import linkedin_id_validator
from lego.utils.test_utils import BaseTestCase


class LinkedinIdValidatorTestCase(BaseTestCase):
    def test_norwegian_letters_in_plain_id(self):
        linkedin_id_validator("åse-olsen")  # å, ø, æ are in À–ɏ range

    def test_full_linkedin_url(self):
        linkedin_id_validator("https://www.linkedin.com/in/john-doe")

    def test_url_with_norwegian_id(self):
        linkedin_id_validator("https://linkedin.com/in/åse-olsen")

    def test_url_with_percent_encoded_norwegian(self):
        linkedin_id_validator("https://linkedin.com/in/%C3%A5se-olsen")  # %C3%A5 = å

    # Reject invalid chars
    def test_invalid_chars_raise(self):
        with self.assertRaises(ValidationError):
            linkedin_id_validator("john@doe")

    # Reject IDs over 70 chars
    def test_too_long_raises(self):
        with self.assertRaises(ValidationError):
            linkedin_id_validator("a" * 71)
