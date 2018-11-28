from rest_framework import serializers

from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory, User
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer


class MembershipSerializer(serializers.ModelSerializer):
    user = PublicUserField(queryset=User.objects.all())

    class Meta:
        model = Membership
        fields = (
            "id",
            "user",
            "abakus_group",
            "role",
            "is_active",
            "email_lists_enabled",
            "created_at",
        )
        read_only_fields = ("created_at", "abakus_group")

    def validate(self, attrs):
        group = AbakusGroup.objects.get(pk=self.context["view"].kwargs["group_pk"])
        return {"abakus_group": group, **attrs}


class PastMembershipSerializer(serializers.ModelSerializer):
    abakus_group = PublicAbakusGroupSerializer()

    class Meta:
        model = MembershipHistory
        fields = ("id", "abakus_group", "role", "start_date", "end_date")
        read_only_fields = ("id", "abakus_group", "role", "start_date", "end_date")
