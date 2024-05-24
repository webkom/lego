from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.lending.models import LendableObject, LendingInstance
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


class DetailedLendableObjectSerializer(BasisModelSerializer):
    image = ImageField(required=False, options={"height": 500})

    class Meta:
        model = LendableObject
        fields = (
            "id",
            "title",
            "description",
            "has_contract",
            "max_lending_period",
            "responsible_groups",
            "responsible_roles",
            "image",
            "location",
            "created_by",
            "updated_by",
        )


class DetailedAdminLendableObjectSerializer(
    ObjectPermissionsSerializerMixin, DetailedLendableObjectSerializer
):
    class Meta:
        model = LendableObject
        fields = (
            DetailedLendableObjectSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )


class LendingInstanceCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = LendingInstance
        fields = (
            "id",
            "lendable_object",
            "start_date",
            "end_date",
            "message",
        )

    def validate(self, data):
        # Check if 'lendable_object', 'start_date', and 'end_date' are provided in the data.
        lendable_object = data.get("lendable_object")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        # Ensure all necessary fields are present
        if lendable_object and start_date and end_date:
            user = self.context["request"].user
            # Check if the user is in one of the responsible groups
            if not user.abakus_groups.filter(
                id__in=lendable_object.responsible_groups.values_list("id", flat=True)
            ).exists():
                # Calculate the lending period and compare
                lending_period = end_date - start_date
                max_lending_period = lendable_object.max_lending_period
                if lending_period > max_lending_period:
                    raise serializers.ValidationError(
                        "Lending period exceeds maximum allowed duration"
                    )

        return data


class DetailedLendingInstanceSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source="created_by")
    lendable_object = DetailedLendableObjectSerializer()

    class Meta:
        model = LendingInstance
        fields = (
            "id",
            "lendable_object",
            "start_date",
            "end_date",
            "author",
            "status",
            "message",
            "created_at",
        )

    def validate(self, data):
        # Check if 'lendable_object', 'start_date', and 'end_date' are provided in the data.
        lendable_object = data.get("lendable_object")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        # Ensure all necessary fields are present
        if lendable_object and start_date and end_date:
            user = self.context["request"].user
            # Check if the user is in one of the responsible groups
            if not user.abakus_groups.filter(
                id__in=lendable_object.responsible_groups.values_list("id", flat=True)
            ).exists():
                # Calculate the lending period and compare
                lending_period = end_date - start_date
                max_lending_period = lendable_object.max_lending_period
                if lending_period > max_lending_period:
                    raise serializers.ValidationError(
                        "Lending period exceeds maximum allowed duration"
                    )

        return data


class DetailedAdminLendingInstanceSerializer(
    ObjectPermissionsSerializerMixin, DetailedLendingInstanceSerializer
):
    class Meta:
        model = LendingInstance
        fields = (
            DetailedLendingInstanceSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )
