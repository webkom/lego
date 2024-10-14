from lego.apps.achievements.models import Achievement
from lego.utils.serializers import BasisModelSerializer


class AchievementSerializer(BasisModelSerializer):
    class Meta:
        model = Achievement
        fields = (
            "id",
            "hidden",
            "created_at",
            "percentage",
            "identifier",
            "level",
        )
