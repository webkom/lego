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


class LendingRequestAdminSerializer(
    ObjectPermissionsSerializerMixin, LendingRequestSerializer
):
    class Meta(LendingRequestSerializer.Meta):
        fields = (
            LendingRequestSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )
