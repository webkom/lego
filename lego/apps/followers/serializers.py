from rest_framework import serializers

from lego.apps.followers.models import FollowEvent, FollowUser
from lego.apps.users.fields import PublicUserField


class FollowerSerializer(serializers.ModelSerializer):

    follower = PublicUserField(read_only=True)

    class Meta:
        fields = (
            'id',
            'follower',
            'target',
        )

    def save(self, **kwargs):
        request = self.context['request']
        kwargs['follower'] = request.user
        return super().save(**kwargs)


class FollowUserSerializer(FollowerSerializer):
    class Meta(FollowerSerializer.Meta):
        model = FollowUser


class FollowEventSerializer(FollowerSerializer):
    class Meta(FollowerSerializer.Meta):
        model = FollowEvent
