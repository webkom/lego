from rest_framework import serializers

from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.memberships import MembershipSerializer
from lego.apps.users.models import GroupText


class GroupTextSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupText
        fields = (
            'text',
        )


class DetailedAbakusGroupSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)
    group_text = GroupTextSerializer(read_only=True)

    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'parent',
            'permissions',
            'memberships',
            'type',
            'group_text',
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
