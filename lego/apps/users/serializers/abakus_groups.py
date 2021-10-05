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

    class Meta:
        model = AbakusGroup
        fields = (
            "id",
            "name",
            "description",
            "contact_email",
            "parent",
            "logo",
            "type",
            "show_badge",
        )


class AbakusGroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbakusGroup
        fields = ("name", "id")


class PublicListAbakusGroupSerializer(PublicAbakusGroupSerializer):
    logo = ImageField(required=False, options={"height": 400, "width": 400})

    class Meta:
        model = AbakusGroup
        fields = PublicAbakusGroupSerializer.Meta.fields + ("number_of_users",)


class PublicDetailedAbakusGroupSerializer(PublicListAbakusGroupSerializer):
    logo = ImageField(required=False, options={"height": 400, "width": 400})

    class Meta:
        model = AbakusGroup
        fields = PublicListAbakusGroupSerializer.Meta.fields + ("text",)
