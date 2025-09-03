from typing import Optional, TypedDict

from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.lending.constants import (
    LENDING_CHOICE_STATUSES,
    LENDING_REQUEST_ADMIN_ACTIONS,
    LENDING_REQUEST_STATUSES,
    LENDING_REQUEST_TRANSLATION_MAP,
    LENDING_REQUEST_USER_ACTIONS,
    CreateLendingRequestType,
)
from lego.apps.lending.models import LendableObject, LendingRequest, TimelineEntry
from lego.apps.lending.notifications import (
    LendingRequestNotification,
    LendingRequestStatusUpdateNotification,
)
from lego.apps.permissions.constants import VIEW
from lego.apps.users.fields import AbakusGroupField
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


class TimelineEntryAttrs(TypedDict, total=False):
    lending_request: LendingRequest
    message: Optional[str]


class LendableObjectSerializer(BasisModelSerializer):
    image = ImageField(required=False, options={"height": 500})
    can_lend = serializers.SerializerMethodField()
    responsible_groups = AbakusGroupField(
        source="can_edit_groups", read_only=True, many=True
    )

    class Meta:
        model = LendableObject
        fields = (
            "id",
            "title",
            "description",
            "image",
            "responsible_groups",
            "location",
            "can_lend",
        )

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


class TimelineEntrySerializer(BasisModelSerializer):
    created_by = PublicUserSerializer()

    class Meta:
        model = TimelineEntry
        fields = (
            "id",
            "created_by",
            "created_at",
            "lending_request",
            "message",
            "status",
            "is_system",
        )


class TimelineEntryCreateAndUpdateSerializer(BasisModelSerializer):

    class Meta:
        model = TimelineEntry
        fields = (
            "id",
            "lending_request",
            "message",
        )

    def validate(self, attrs: TimelineEntryAttrs):
        attrs = super().validate(attrs)
        lending_request: LendingRequest = attrs.get("lending_request")
        user: User = self.context["request"].user
        if not lending_request._meta.permission_handler.has_object_permissions(
            user, VIEW, lending_request
        ):
            raise serializers.ValidationError(
                {"status": "You are not permitted to update this request."}
            )
        return attrs


class LendingRequestListSerializer(BasisModelSerializer):
    status = serializers.ChoiceField(choices=LENDING_CHOICE_STATUSES, required=False)
    lendable_object = LendableObjectSerializer(read_only=True)

    class Meta:
        model = LendingRequest
        fields = (
            "id",
            "lendable_object",
            "status",
            "start_date",
            "end_date",
        )


class LendingRequestDetailSerializer(BasisModelSerializer):
    status = serializers.ChoiceField(choices=LENDING_CHOICE_STATUSES, required=False)
    created_by = PublicUserSerializer(read_only=True)
    updated_by = PublicUserSerializer(read_only=True)
    lendable_object = LendableObjectSerializer(read_only=True)
    timeline_entries = TimelineEntrySerializer(many=True, read_only=True)

    class Meta:
        model = LendingRequest
        fields = (
            "id",
            "created_by",
            "updated_by",
            "lendable_object",
            "status",
            "text",
            "start_date",
            "end_date",
            "timeline_entries",
        )


class LendingRequestCreateAndUpdateSerializer(BasisModelSerializer):
    status = serializers.ChoiceField(choices=LENDING_CHOICE_STATUSES, required=False)
    created_by = PublicUserSerializer(read_only=True)
    updated_by = PublicUserSerializer(read_only=True)
    lendable_object = LendableObjectField(queryset=LendableObject.objects.all())
    timeline_entries = TimelineEntrySerializer(many=True, read_only=True)

    class Meta:
        model = LendingRequest
        fields = (
            "id",
            "created_by",
            "updated_by",
            "lendable_object",
            "status",
            "text",
            "start_date",
            "end_date",
            "timeline_entries",
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
            if "status" in attrs and attrs["status"] not in (
                LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"],
                None,
            ):
                raise serializers.ValidationError(
                    {"status": "On create, status must be 'unapproved'."}
                )
            attrs["status"] = LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"]

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
                    LENDING_REQUEST_STATUSES["LENDING_CANCELLED"]["value"],
                    LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"],
                ):
                    raise serializers.ValidationError(
                        {
                            "status": (
                                "You cannot change the status to that value. "
                                "You can only set it to 'cancelled' or 'unapproved'."
                            )
                        }
                    )
                if (
                    self.instance.created_by != user
                    and new_status
                    == LENDING_REQUEST_STATUSES["LENDING_CANCELLED"]["value"]
                ):
                    raise serializers.ValidationError(
                        {"status": ("You cannot cancel someone else's request.. ")}
                    )
            if self.instance.created_by != user and attrs.get("text"):
                raise serializers.ValidationError(
                    {"text": ("You cannot edit someone else's request.. ")}
                )

        return attrs

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", old_status)
        instance = super().update(instance, validated_data)
        if new_status != old_status:
            if new_status == LENDING_REQUEST_STATUSES["LENDING_CHANGES_RESOLVED"]["value"] and old_status != LENDING_REQUEST_STATUSES["LENDING_CHANGES_REQUESTED"]["value"]:
                raise serializers.ValidationError(
                    {"status": ("You can not resolve a request that doesn't have changes requested")}
                )

            new_status_string = LENDING_REQUEST_TRANSLATION_MAP[new_status]
            timelineentry = TimelineEntry.objects.create(
                message=new_status_string,
                lending_request=instance,
                current_user=self.context.get("request").user,
                is_system=True,
                status=new_status,
            )
            if new_status in LENDING_REQUEST_ADMIN_ACTIONS:
                notification = LendingRequestStatusUpdateNotification(
                    instance.created_by,
                    lending_request=instance,
                    timelineentry=timelineentry,
                    recipient=instance.created_by,
                )
                notification.notify()
            elif new_status in LENDING_REQUEST_USER_ACTIONS:
                for lender in instance.lendable_object.can_edit_users.all():
                    notification = LendingRequestStatusUpdateNotification(
                        lender,
                        lending_request=instance,
                        timelineentry=timelineentry,
                        recipient=lender,
                    )
                    notification.notify()

        return instance

    def create(self, validated_data: CreateLendingRequestType) -> LendingRequest:
        instance: LendingRequest = super().create(validated_data)

        TimelineEntry.objects.create(
            message=LENDING_REQUEST_TRANSLATION_MAP[
                LENDING_REQUEST_STATUSES["LENDING_CREATED"]["value"]
            ],
            lending_request=instance,
            current_user=self.context.get("request").user,
            is_system=True,
            status=LENDING_REQUEST_STATUSES["LENDING_CREATED"]["value"],
        )

        for lender in instance.lendable_object.can_edit_users.all():
            notification = LendingRequestNotification(
                instance.created_by, lending_request=instance, lender=lender
            )
            notification.notify()
        return instance
