from lego.apps.events.models import Event
from lego.apps.events.serializers.events import EventSearchSerializer
from lego.apps.search import register
from lego.apps.search.index import SearchIndex


class EventModelIndex(SearchIndex):
    queryset = Event.objects.all()
    serializer_class = EventSearchSerializer
    result_fields = (
        "title",
        "description",
        "text",
        "cover",
        "location",
        "start_time",
        "end_time",
    )
    autocomplete_result_fields = ("title", "start_time")

    autocomplete_fields = ("title",)
    search_fields = ("title", "description", "text")

    search_ordering = ("-start_time",)
    autocomplete_ordering = ("-start_time",)


register(EventModelIndex)
