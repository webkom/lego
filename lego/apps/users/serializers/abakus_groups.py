from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, Membership
from lego.apps.users.serializers.memberships import MembershipSerializer


class DetailedAbakusGroupSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)
    logo = ImageField(required=False, options={'height': 400, 'width': 400})

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
            'text',
            'logo',
        )

    def create(self, validated_data):
        group = super(DetailedAbakusGroupSerializer, self).create(validated_data)
        user = self.context['request'].user
        Membership.objects.create(**{
            'user': user,
            'abakus_group': group,
            'role': constants.LEADER,
        })
        return group


class PublicAbakusGroupSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)
    logo = ImageField(required=False, options={'height': 400, 'width': 400})

    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'memberships',
            'parent',
            'logo'
        )
