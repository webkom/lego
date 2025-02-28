from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.lending.constants import LENDING_CHOICE_STATUSES
from lego.apps.lending.models import LendableObject, LendingRequest
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


class LendableObjectSerializer(BasisModelSerializer):
    image = ImageField(required=False, options={"height": 500})
    can_lend = serializers.SerializerMethodField()

    class Meta:
        model = LendableObject
        fields = ("id", "title", "description", "image", "location", "can_lend")

    def get_can_lend(self, obj):
        return obj.can_lend(self.context["request"].user)


class LendableObjectAdminSerializer(
    ObjectPermissionsSerializerMixin, LendableObjectSerializer
):
    class Meta(LendableObjectSerializer.Meta):
        fields = (
            LendableObjectSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )


class LendingRequestSerializer(BasisModelSerializer):
    status = serializers.ChoiceField(
        choices=LENDING_CHOICE_STATUSES, required=False
    )

    class Meta:
        model = LendingRequest
        fields = (
            "created_by",
            "updated_by",
            "lendable_object",
            "status",
            "start_date",
            "end_date",
        )

    def validate(self, attrs):
        """
        Custom validation for lending requests:
        - Ensures start_date is before end_date.
        - Ensures the lending object is available for lending.
        - Ensures the user has permission to create the request.
        """
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        lendable_object = attrs.get("lendable_object")
        user = self.context["request"].user

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        if lendable_object and not lendable_object.can_lend(user):
            raise serializers.ValidationError(
                {"lendable_object": "You do not have permission to lend this object."}
            )

        return super().validate(attrs)
    
class LendingRequestAdminSerializer(
    ObjectPermissionsSerializerMixin, LendingRequestSerializer
):
    class Meta(LendingRequestSerializer.Meta):
        fields = (
            LendingRequestSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )
