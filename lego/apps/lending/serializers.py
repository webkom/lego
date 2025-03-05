from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.lending.constants import LENDING_CHOICE_STATUSES
from lego.apps.lending.models import LendableObject, LendingRequest
from lego.apps.users.serializers.users import PublicUserSerializer
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


class LendableObjectField(serializers.PrimaryKeyRelatedField):
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        serializer = LendableObjectSerializer(instance=value, context=self.context)
        return serializer.data


class LendingRequestSerializer(BasisModelSerializer):
    status = serializers.ChoiceField(choices=LENDING_CHOICE_STATUSES, required=False)
    created_by = PublicUserSerializer(read_only=True)
    updated_by = PublicUserSerializer(read_only=True)
    lendable_object = LendableObjectSerializer(read_only=True)

    class Meta:
        model = LendingRequest
        fields = (
            "id",
            "created_by",
            "updated_by",
            "lendable_object",
            "status",
            "start_date",
            "end_date",
        )


class LendingRequestCreateAndUpdateSerializer(BasisModelSerializer):
    status = serializers.ChoiceField(choices=LENDING_CHOICE_STATUSES, required=False)
    created_by = PublicUserSerializer(read_only=True)
    updated_by = PublicUserSerializer(read_only=True)
    lendable_object = LendableObjectField(queryset=LendableObject.objects.all())

    class Meta:
        model = LendingRequest
        fields = (
            "id",
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
        - Ensures the user has permission to create or modify the request.
        - If it is a create request, status must be "unapproved".
        - If it is an edit request, and the user does NOT have 'edit' permission
          on the LendableObject, the status can only be "cancelled" or "unapproved".
        """
        attrs = super().validate(attrs)

        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        lendable_object = attrs.get("lendable_object") or getattr(
            self.instance, "lendable_object", None
        )
        user = self.context["request"].user

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        if lendable_object and not lendable_object.can_lend(user):
            raise serializers.ValidationError(
                {"lendable_object": "You do not have permission to lend this object."}
            )

        if self.instance is None:
            if "status" in attrs and attrs["status"] not in ("unapproved", None):
                raise serializers.ValidationError(
                    {"status": "On create, status must be 'unapproved'."}
                )
            attrs["status"] = "unapproved"

        else:
            if "status" in attrs:
                new_status = attrs["status"]

                user_in_edit_group = False
                if lendable_object:
                    group_ids = [group.pk for group in user.all_groups]
                    user_in_edit_group = lendable_object.can_edit_groups.filter(
                        pk__in=group_ids
                    ).exists()

                if not user_in_edit_group and new_status not in (
                    "cancelled",
                    "unapproved",
                ):
                    raise serializers.ValidationError(
                        {
                            "status": (
                                "You cannot change the status to that value. "
                                "You can only set it to 'cancelled' or 'unapproved'."
                            )
                        }
                    )

        return attrs
