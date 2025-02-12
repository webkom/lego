from rest_framework import serializers

from lego.apps.achievements.models import Achievement
from lego.utils.serializers import BasisModelSerializer


class AchievementSerializer(BasisModelSerializer):
    class Meta:
        model = Achievement
        fields = (
            "id",
            "updated_at",
            "percentage",
            "identifier",
            "level",
        )


class KeypressOrderSerializer(serializers.Serializer):
    code = serializers.ListField(
        child=serializers.IntegerField(),
    )
