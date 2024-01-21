from rest_framework import serializers

from lego.apps.events.fields import PublicEventField
from lego.apps.events.models import Event
from lego.apps.users.models import Penalty


class PenaltySerializer(serializers.ModelSerializer):
    source_event = PublicEventField(queryset=Event.objects.all(), required=False)

    class Meta:
        model = Penalty
        fields = (
            "id",
            "created_at",
            "user",
            "reason",
            "weight",
            "source_event",
            "exact_expiration",
        )
