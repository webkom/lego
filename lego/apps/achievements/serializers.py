from lego.apps.achievements.models import Achievement
from lego.apps.achievements.utils.calculation_utils import calculate_user_rank
from lego.utils.serializers import BasisModelSerializer
from rest_framework import serializers


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
