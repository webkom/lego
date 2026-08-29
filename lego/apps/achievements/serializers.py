from rest_framework import serializers

from lego.apps.achievements.models import Achievement, RankSnapshot
from lego.utils.serializers import BasisModelSerializer


class AchievementSerializer(BasisModelSerializer):
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = (
            "id",
            "updated_at",
            "percentage",
            "identifier",
            "level",
        )

    def get_percentage(self, obj):
        # rarity_lookup is precomputed once per request (see get_serializer_context
        # on LeaderBoardViewSet/UsersViewSet) instead of one query per achievement -
        # fall back to the property when a caller hasn't set it up.
        rarity_lookup = self.context.get("rarity_lookup")
        if rarity_lookup is not None:
            cached = rarity_lookup.get((obj.identifier, obj.level))
            if cached is not None:
                return cached
        return round(obj.percentage, 2)


class RankSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankSnapshot
        fields = ("date", "rank", "value")


class KeypressOrderSerializer(serializers.Serializer):
    code = serializers.ListField(
        child=serializers.IntegerField(),
    )
