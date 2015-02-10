from lego.app.events.models import Event
from lego.utils.base_serializer import BasisSerializer


class EventSerializer(BasisSerializer):
    class Meta:
        model = Event
