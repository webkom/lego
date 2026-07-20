from typing import Any

from rest_framework import serializers

from lego.apps.users import constants
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory, User
from lego.apps.users.permissions import EDIT_ROLES
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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        group = AbakusGroup.objects.get(pk=self.context["view"].kwargs["group_pk"])
        instance = self.instance if isinstance(self.instance, Membership) else None
        if instance is not None and "user" in attrs and attrs["user"] != instance.user:
            raise serializers.ValidationError(
                {"user": "Cannot change the user of a membership."}
            )
        demotes_last_leader = (
            instance is not None
            and group.type == constants.GROUP_INTEREST
            and group.active
            and instance.role == constants.LEADER
            and attrs.get("role") == constants.CO_LEADER
            and attrs.get("is_active", instance.is_active)
            and not Membership.objects.filter(
                abakus_group=group, is_active=True, role__in=EDIT_ROLES
            )
            .exclude(pk=instance.pk)
            .exists()
        )
        if demotes_last_leader:
            raise serializers.ValidationError(
                {
                    "role": "Interest groups must have a leader. Promote someone else first."
                }
            )
        return {"abakus_group": group, **attrs}


class PastMembershipSerializer(serializers.ModelSerializer):
    abakus_group = PublicAbakusGroupSerializer()

    class Meta:
        model = MembershipHistory
        fields = ("id", "abakus_group", "role", "start_date", "end_date")
        read_only_fields = ("id", "abakus_group", "role", "start_date", "end_date")
