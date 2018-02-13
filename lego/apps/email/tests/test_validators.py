from unittest import mock

from django.core.exceptions import ValidationError

from lego.apps.email.models import EmailAddress
from lego.apps.email.validators import validate_email_address
from lego.utils.test_utils import BaseTestCase


class ValidatorsTestCase(BaseTestCase):
    @mock.patch('lego.apps.email.models.EmailAddress.is_assigned', return_value=True)
    def test_email_address_validator(self, mock_is_assigned):
        """The validator should raise ValidationError if is_assigned returns True"""
        email_address = EmailAddress.objects.create(email='test')

        self.assertRaises(ValidationError, validate_email_address, email_address)

        mock_is_assigned.assert_called_once_with()
