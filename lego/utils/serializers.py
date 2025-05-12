from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from rest_framework import serializers

from lego.apps.users.fields import AbakusGroupField, PublicUserField
from lego.apps.users.models import AbakusGroup, User
from lego.utils.content_types import instance_to_string, string_to_instance


class GenericRelationField(serializers.CharField):
    default_error_messages = {
        "does_not_exist": "Invalid model data <{data}> - object does not exist.",
        "incorrect_type": 'Source should be in the form "[AppLabel].[ModelName]-[ObjectId]"',
        "multiple_objects_returned": "Multiple objects returned, contact admin.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        try:
            return instance_to_string(value)
        except Exception:
            pass

    def to_internal_value(self, data):
        try:
            return string_to_instance(data)
        except (TypeError, ValueError):
            self.fail("incorrect_type")
        except ObjectDoesNotExist:
            self.fail("does_not_exist", data=data)
        except MultipleObjectsReturned:
            self.fail("multiple_objects_returned")


class BasisModelSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        request = self.context["request"]
        kwargs["current_user"] = request.user
        super().save(**kwargs)


class ObjectPermissionsSerializerMixin(serializers.Serializer):
    class Meta:
        fields = (
            "can_edit_users",
            "can_view_groups",
            "can_edit_groups",
            "require_auth",
        )

    can_edit_users = PublicUserField(
        queryset=User.objects.all(), allow_null=True, required=False, many=True
    )
    can_edit_groups = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), allow_null=True, required=False, many=True
    )
    can_view_groups = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), allow_null=True, required=False, many=True
    )
