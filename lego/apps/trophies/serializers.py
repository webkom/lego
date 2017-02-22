from rest_framework import serializers

from lego.apps.trophies.models import Trophy, UserTrophy


class TrophySerializer(serializers.ModelSerializer):
    class Meta:
        model = Trophy
        fields = (
            'id',
            'title',
            'description',
            'points',
            'content_type'
        )


class UserTrophySerializer(serializers.ModelSerializer):
    user = TrophySerializer(many=False, read_only=True)

    class Meta:
        model = UserTrophy
        fields = (
            'id',
            'award_date',
            'trophy'
        )
