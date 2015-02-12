from basis.serializers import BasisSerializer

from lego.app.flatpages.models import Page


class EventSerializer(BasisSerializer):
    class Meta:
        model = Page
