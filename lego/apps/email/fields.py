from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lego.apps.email.validators import validate_email_address, validate_email_address_content


class EmailAddressField(serializers.PrimaryKeyRelatedField):
    """
    Manage the email address as a string.
    """

    def __init__(self, **kwargs):
        validators = kwargs.get('validators')
        kwargs['validators'] = validators if validators is not None else [validate_email_address]
        kwargs['validators'].append(validate_email_address_content)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        """
        Create email if not exists.
        """
        try:
            email_address, _ = self.get_queryset().get_or_create(pk=data)
            return email_address
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)
