from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from rest_framework import serializers

from lego.utils.content_types import string_to_instance


class GenericRelationField(serializers.CharField):

    default_error_messages = {
        'does_not_exist': 'Invalid model data <{data}> - object does not exist.',
        'incorrect_type': 'Source should be in the form "[AppLabel].[ModelName]-[ObjectId]"',
        'multiple_objects_returned': 'Multiple objects returned, contact admin.'
    }

    def __init__(self, *args, **kwargs):
        kwargs['write_only'] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        return None

    def to_internal_value(self, data):
        try:
            return string_to_instance(data)
        except (TypeError, ValueError):
            self.fail('incorrect_type')
        except ObjectDoesNotExist:
            self.fail('does_not_exist', data=data)
        except MultipleObjectsReturned:
            self.fail('multiple_objects_returned')


class BasisModelSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        request = self.context['request']
        kwargs['current_user'] = request.user
        super().save(**kwargs)
