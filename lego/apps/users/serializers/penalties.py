from rest_framework import serializers

from lego.apps.users.models import Penalty


class PenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty
        fields = (
            'id', 'user', 'reason', 'weight', 'source_event'
        )
