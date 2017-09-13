from rest_framework import serializers

from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import AbakusGroup, Membership, User


class MembershipSerializer(serializers.ModelSerializer):
    user = PublicUserField(queryset=User.objects.all())

    class Meta:
        model = Membership
        fields = (
            'id',
            'user',
            'abakus_group',
            'role',
            'is_active',
            'start_date',
            'end_date',
        )


class MembershipGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = (
            'user',
            'role',
        )


class MembershipSetMembershipSerializer(serializers.ModelSerializer):
    memberships = MembershipGroupSerializer(many=True)

    class Meta:
        model = AbakusGroup
        fields = (
            'memberships'
        )
