from rest_framework import serializers

from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.memberships import MembershipSerializer


class DetailedAbakusGroupSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)

    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'parent',
            'permissions',
            'memberships'
        )


class PublicAbakusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'parent'
        )
