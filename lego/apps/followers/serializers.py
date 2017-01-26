from rest_framework import serializers

from lego.apps.followers.models import Follower


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = (
            'id',
            'follower',
            'following'
        )