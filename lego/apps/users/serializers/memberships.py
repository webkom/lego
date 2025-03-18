from rest_framework import serializers

from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory, User
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer


class MembershipSerializer(serializers.ModelSerializer):
    user = PublicUserField(queryset=User.objects.all())
    first_join_date = serializers.SerializerMethodField()

    def get_first_join_date(self, obj):
        """
        Retrieve the earliest date the user joined the given abakus_group
        from either Membership or MembershipHistory.
        """
        user = obj.user
        group = obj.abakus_group

        membership_date = (
            Membership.objects.filter(user=user, abakus_group=group)
            .values_list("created_at", flat=True)
            .order_by("created_at")
            .first()
        )
        membership_date = membership_date.date() if membership_date else None

        history_date = (
            MembershipHistory.objects.filter(user=user, abakus_group=group)
            .values_list("start_date", flat=True)
            .order_by("start_date")
            .first()
        )

        dates = list(filter(None, [membership_date, history_date]))
        return min(dates) if dates else None

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
            "first_join_date",
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
