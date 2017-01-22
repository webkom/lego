from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

"""
This utilities is used to retrieve model from a content string and opposite.
A content string defines a model instance and we can use this to retrieve objects from the database.
Content strings is on the form "<app_label>.<model_name>-<instance_pk>".
"""

VALIDATION_EXCEPTIONS = (ValueError, TypeError, ObjectDoesNotExist, MultipleObjectsReturned)


def split_string(instance_string):
    """
    Split a string like app_label.model_name-instance_pk to app_label.model_name, instance_pk
    We need to handle multiple `-` inside the instance_pk, this is why this function looks ugly.
    """
    content_splitpoint = instance_string.index('-')
    if not content_splitpoint:
        raise ValueError
    content_type_string = instance_string[:content_splitpoint]
    id_string = instance_string[content_splitpoint + 1:]
    return content_type_string, id_string


def string_to_model_cls(content_type_string):
    """
    Convert a string like app_label.model_name to a model cls
    """
    app_label, model_name = content_type_string.split('.')
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    return content_type.model_class()


def string_to_instance(instance_string):
    """
    Convert a string like app_label.model_name-instance_pk to a model instance
    """
    content_type_string, id_string = split_string(instance_string)

    app_label, model_name = content_type_string.split('.')
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    return content_type.get_object_for_this_type(pk=id_string)


def instance_to_content_type_string(instance):
    """
    Convert a model instance to a string like app_label.model_name
    """
    return f'{instance._meta.app_label}.{instance._meta.model_name}'


def instance_to_string(instance):
    """
    Convert a model instance to a string like app_label.model_name-instance_pk
    """
    content_type = instance_to_content_type_string(instance)
    return f'{content_type}-{instance.pk}'
