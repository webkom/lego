from rest_framework import serializers

from lego.apps.users.models import AbakusGroup

from .users import PublicUserSerializer


class DetailedAbakusGroupSerializer(serializers.ModelSerializer):
    users = PublicUserSerializer(many=True, read_only=True)

    class Meta:
        model = AbakusGroup
        fields = (
            'id',
            'name',
            'description',
            'parent',
            'permissions',
            'users'
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
