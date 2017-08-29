from rest_framework import serializers

from lego.apps.users.models import Membership
from lego.apps.users.serializers.users import PublicUserSerializer


class MembershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = (
            'user',
            'abakus_group',
            'role',
            'is_active',
            'start_date',
            'end_date'
        )


class MembershipSerializer(MembershipCreateSerializer):
    user = PublicUserSerializer(many=False, read_only=True)
