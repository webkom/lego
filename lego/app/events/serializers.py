from basis.serializers import BasisSerializer

from lego.app.events.models import Event


class EventSerializer(BasisSerializer):
    class Meta:
        model = Event
