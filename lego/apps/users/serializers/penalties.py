from rest_framework import serializers

from lego.apps.users.models import PenaltyGroup


class PenaltyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenaltyGroup
        fields = (
            "id",
            "created_at",
            "user",
            "reason",
            "weight",
            "source_event",
            "activation_time",
            "exact_expiration",
        )
