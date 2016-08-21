from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text


"""
This utilities is used to retrieve model from a content string and opposite.
A content string defines a model instance and we can use this to retrieve objects from the database.
Content strings is on the form "<app_label>.<model_name>-<instance_id>".
"""


def string_to_instance(content_string):
    content_type_string, id_string = content_string.split('-')
    app_label, model_name = content_type_string.split('.')
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    return content_type.get_object_for_this_type(id=id_string)


def instance_to_content_type_string(instance):
    return '{app_label}.{model_name}'.format(
        app_label=instance._meta.app_label,
        model_name=instance._meta.model_name
    )


def instance_to_string(instance):
    return '{content_type}-{instance_id}'.format(
        content_type=instance_to_content_type_string(instance),
        instance_id=force_text(instance.id)
    )
