from rest_framework import serializers

from lego.apps.users.models import Membership
from lego.apps.users.serializers.users import PublicUserSerializer


class MembershipSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(many=False, read_only=True)

    class Meta:
        model = Membership
        fields = (
            'user',
            'abakus_group_id',
            'role',
            'is_active',
            'start_date',
            'end_date'
        )
