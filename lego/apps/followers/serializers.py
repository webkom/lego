from rest_framework import serializers

from lego.apps.followers.models import Follower, FollowEvent, FollowUser
from lego.apps.users.serializers.users import PublicUserSerializer


class FollowerSerializer(serializers.ModelSerializer):
    follower = PublicUserSerializer()

    class Meta:
        model = Follower
        fields = (
            'id',
            'follower',
        )


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUser
        fields = (
            'id',
            'follower',
            'follow_target',
        )


class FollowEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowEvent
        fields = (
            'id',
            'follower',
            'follow_target',
        )


"""
class FollowCompanySerializer(serializers.ModelSerializer):
    follow_target = COMPANY SERIALIZER HERE

    class Meta:
        model = FollowCompany
        fields = (
            'id',
            'follower',
            'follow_target',
        )
"""
