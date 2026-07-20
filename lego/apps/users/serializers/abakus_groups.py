from typing import Any

from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, Membership


class DetailedAbakusGroupSerializer(serializers.ModelSerializer):
    logo = ImageField(
        required=False, allow_null=True, options={"height": 400, "width": 400}
    )

    class Meta:
        model = AbakusGroup
        fields = (
            "id",
            "name",
            "description",
            "contact_email",
            "parent",
            "permissions",
            "parent_permissions",
            "type",
            "text",
            "logo",
            "number_of_users",
            "show_badge",
            "active",
        )

    def create(self, validated_data):
        if validated_data.get("type", None) == "interesse":
            validated_data["parent"] = AbakusGroup.objects.get(name="Interessegrupper")
        group = super(DetailedAbakusGroupSerializer, self).create(validated_data)
        user = self.context["request"].user
        Membership.objects.create(
            **{"user": user, "abakus_group": group, "role": constants.LEADER}
        )
        return group


class PublicAbakusGroupSerializer(serializers.ModelSerializer):
    logo = ImageField(required=False, options={"height": 400, "width": 400})
    logo_placeholder = ImageField(
        source="logo",
        required=False,
        options={"height": 40, "width": 40, "filters": ["blur(20)"]},
    )

    class Meta:
        model = AbakusGroup
        fields = (
            "id",
            "name",
            "description",
            "contact_email",
            "parent",
            "logo",
            "logo_placeholder",
            "type",
            "show_badge",
            "active",
        )


class AbakusGroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbakusGroup
        fields = ("name", "id")


class UserMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ("id", "role")


class PublicListAbakusGroupSerializer(PublicAbakusGroupSerializer):
    logo = ImageField(required=False, options={"height": 400, "width": 400})
    user_membership = serializers.SerializerMethodField()

    class Meta:
        model = AbakusGroup
        fields = PublicAbakusGroupSerializer.Meta.fields + (
            "number_of_users",
            "user_membership",
        )

    def get_user_membership(self, group: AbakusGroup) -> dict[str, Any] | None:
        if hasattr(group, "user_membership"):
            membership = group.user_membership[0] if group.user_membership else None
        else:
            request = self.context.get("request", None)
            if not request or not request.user.is_authenticated:
                return None
            membership = Membership.objects.filter(
                abakus_group=group, user=request.user, is_active=True
            ).first()
        if not membership:
            return None
        return UserMembershipSerializer(membership).data


class PublicDetailedAbakusGroupSerializer(PublicListAbakusGroupSerializer):
    logo = ImageField(required=False, options={"height": 400, "width": 400})

    class Meta:
        model = AbakusGroup
        fields = PublicListAbakusGroupSerializer.Meta.fields + ("text",)
