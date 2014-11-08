# -*- coding: utf8 -*-

from django.core.validators import validate_email, ValidationError


def validate_local_part(value):
    try:
        validate_email('%s@abakus.no' % value)
    except ValidationError:
        raise ValidationError('Invalid local part.')
