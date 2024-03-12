from django.forms import ValidationError


def responsible_roles_validator(value):
    if len(value) != len(set(value)):
        raise ValidationError("Duplicate values are not allowed.")
