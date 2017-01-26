from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Event
from .serializers import EventReadSerializer


class EventModelIndex(SearchIndex):

    queryset = Event.objects.all()
    serializer_class = EventReadSerializer
    result_fields = ('title', 'description', 'text', 'cover', 'location', 'start_time', 'end_time')
    autocomplete_result_fields = ('title', 'start_time')

    def get_autocomplete(self, instance):
        return instance.title


register(EventModelIndex)
